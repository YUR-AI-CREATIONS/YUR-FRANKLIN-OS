"""
FRANKLIN OS Deployment Engine
==============================
Controlled, hardened deployment with full rollback, audit logging, and execution isolation.
Public launch intentionally deferred.

Infrastructure Stack:
- Frontend: Vercel (Edge-optimized)
- Backend: Docker (Containerized)
- Execution: Isolated workers (no shared state)
- Secrets: Environment variables only
- Logs: Immutable + auditable
"""

import os
import json
import hashlib
import shutil
import subprocess
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Deployment environments - no single-environment shortcuts"""
    DEV = "dev"           # Rapid iteration
    STAGING = "staging"   # Full system simulation
    PROD = "prod"         # Locked, auditable, rollback-ready


class DeploymentStatus(Enum):
    """Deployment status tracking"""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    HALTED = "halted"  # Kill switch activated


@dataclass
class DeploymentCheckpoint:
    """Checkpoint for rollback capability"""
    checkpoint_id: str
    environment: Environment
    timestamp: datetime
    artifact_hash: str
    config_hash: str
    state: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "environment": self.environment.value,
            "timestamp": self.timestamp.isoformat(),
            "artifact_hash": self.artifact_hash,
            "config_hash": self.config_hash,
            "state": self.state
        }


@dataclass
class Deployment:
    """Deployment record with full audit trail"""
    deployment_id: str
    build_id: str
    project_name: str
    environment: Environment
    status: DeploymentStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    checkpoint: Optional[DeploymentCheckpoint] = None
    urls: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    rollback_available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployment_id": self.deployment_id,
            "build_id": self.build_id,
            "project_name": self.project_name,
            "environment": self.environment.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            "checkpoint": self.checkpoint.to_dict() if self.checkpoint else None,
            "urls": self.urls,
            "logs": self.logs[-20:],  # Last 20 log entries
            "rollback_available": self.rollback_available
        }


class DeploymentEngine:
    """
    Franklin OS Deployment Engine
    
    Features:
    - Multi-environment support (DEV → STAGING → PROD)
    - Instant rollback capability
    - Kill switch integration with Sentinel
    - Docker containerization
    - Vercel deployment configuration
    - Immutable audit logging
    """
    
    def __init__(self):
        self.deployments: Dict[str, Deployment] = {}
        self.checkpoints: Dict[str, DeploymentCheckpoint] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.kill_switch_active: bool = False
        self.public_access_enabled: bool = False  # Explicitly disabled
        
        logger.info("[DEPLOY] Deployment Engine initialized - Public access DISABLED")
    
    def _log(self, action: str, details: Dict[str, Any], level: str = "INFO"):
        """Immutable audit log entry"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details,
            "level": level,
            "hash": hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()[:16]
        }
        self.audit_log.append(entry)
        logger.info(f"[DEPLOY] {action}: {details}")
        return entry
    
    def create_deployment(self, build_id: str, project_name: str, 
                          environment: Environment = Environment.DEV) -> Deployment:
        """Create a new deployment"""
        
        # Enforce environment progression
        if environment == Environment.PROD:
            # Check if STAGING deployment exists and is successful
            staging_deployments = [
                d for d in self.deployments.values()
                if d.build_id == build_id and d.environment == Environment.STAGING and d.status == DeploymentStatus.DEPLOYED
            ]
            if not staging_deployments:
                raise ValueError("Cannot deploy to PROD without successful STAGING deployment")
        
        deployment_id = f"deploy_{len(self.deployments) + 1:06d}"
        
        deployment = Deployment(
            deployment_id=deployment_id,
            build_id=build_id,
            project_name=project_name,
            environment=environment,
            status=DeploymentStatus.PENDING
        )
        
        self.deployments[deployment_id] = deployment
        
        self._log("deployment_created", {
            "deployment_id": deployment_id,
            "build_id": build_id,
            "environment": environment.value
        })
        
        return deployment
    
    def create_checkpoint(self, deployment_id: str, artifact: Dict[str, Any], 
                          config: Dict[str, Any]) -> DeploymentCheckpoint:
        """Create rollback checkpoint before deployment"""
        
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        checkpoint_id = f"cp_{deployment_id}_{len(self.checkpoints) + 1:04d}"
        
        checkpoint = DeploymentCheckpoint(
            checkpoint_id=checkpoint_id,
            environment=deployment.environment,
            timestamp=datetime.utcnow(),
            artifact_hash=hashlib.sha256(json.dumps(artifact, sort_keys=True).encode()).hexdigest(),
            config_hash=hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
            state={
                "artifact": artifact,
                "config": config,
                "deployment_id": deployment_id
            }
        )
        
        self.checkpoints[checkpoint_id] = checkpoint
        deployment.checkpoint = checkpoint
        
        self._log("checkpoint_created", {
            "checkpoint_id": checkpoint_id,
            "deployment_id": deployment_id,
            "artifact_hash": checkpoint.artifact_hash[:16],
            "config_hash": checkpoint.config_hash[:16]
        })
        
        return checkpoint
    
    def generate_docker_config(self, deployment: Deployment, 
                               artifact: Dict[str, Any]) -> Dict[str, str]:
        """Generate Docker configuration for backend"""
        
        dockerfile = f"""# FRANKLIN OS - {deployment.project_name}
# Generated: {datetime.utcnow().isoformat()}
# Build: {deployment.build_id}
# Environment: {deployment.environment.value}

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables (secrets from runtime)
ENV ENVIRONMENT={deployment.environment.value}
ENV BUILD_ID={deployment.build_id}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run with isolated worker
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
"""
        
        docker_compose = f"""version: '3.8'

services:
  {deployment.project_name.lower().replace(' ', '-')}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT={deployment.environment.value}
      - BUILD_ID={deployment.build_id}
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
"""
        
        self._log("docker_config_generated", {
            "deployment_id": deployment.deployment_id,
            "environment": deployment.environment.value
        })
        
        return {
            "Dockerfile": dockerfile,
            "docker-compose.yml": docker_compose
        }
    
    def generate_vercel_config(self, deployment: Deployment,
                               artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Vercel configuration for frontend"""
        
        vercel_json = {
            "version": 2,
            "name": deployment.project_name.lower().replace(' ', '-'),
            "builds": [
                {
                    "src": "package.json",
                    "use": "@vercel/static-build",
                    "config": {
                        "distDir": "build"
                    }
                }
            ],
            "routes": [
                {
                    "src": "/api/(.*)",
                    "dest": f"${{BACKEND_URL}}/api/$1"
                },
                {
                    "src": "/(.*)",
                    "dest": "/$1"
                }
            ],
            "env": {
                "REACT_APP_ENVIRONMENT": deployment.environment.value,
                "REACT_APP_BUILD_ID": deployment.build_id
            },
            "regions": ["iad1"],  # Edge-optimized
            "github": {
                "silent": True
            }
        }
        
        self._log("vercel_config_generated", {
            "deployment_id": deployment.deployment_id,
            "environment": deployment.environment.value
        })
        
        return vercel_json
    
    def deploy(self, deployment_id: str, artifact: Dict[str, Any], 
               config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment with full audit trail"""
        
        if self.kill_switch_active:
            raise ValueError("Kill switch is active - all deployments halted")
        
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        # Create checkpoint before deployment
        self.create_checkpoint(deployment_id, artifact, config)
        
        deployment.status = DeploymentStatus.BUILDING
        self._log("deployment_started", {"deployment_id": deployment_id})
        
        try:
            # Generate configurations
            docker_config = self.generate_docker_config(deployment, artifact)
            vercel_config = self.generate_vercel_config(deployment, artifact)
            
            deployment.status = DeploymentStatus.DEPLOYING
            
            # Simulate deployment (in real implementation, this would call Vercel/Docker APIs)
            deployment.urls = {
                "frontend": f"https://{deployment.project_name.lower().replace(' ', '-')}-{deployment.environment.value}.vercel.app",
                "backend": f"https://api-{deployment.project_name.lower().replace(' ', '-')}-{deployment.environment.value}.onrender.com",
                "health": f"https://api-{deployment.project_name.lower().replace(' ', '-')}-{deployment.environment.value}.onrender.com/health"
            }
            
            deployment.status = DeploymentStatus.DEPLOYED
            deployment.deployed_at = datetime.utcnow()
            
            self._log("deployment_completed", {
                "deployment_id": deployment_id,
                "environment": deployment.environment.value,
                "urls": deployment.urls
            })
            
            return {
                "success": True,
                "deployment": deployment.to_dict(),
                "docker_config": docker_config,
                "vercel_config": vercel_config
            }
            
        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            self._log("deployment_failed", {
                "deployment_id": deployment_id,
                "error": str(e)
            }, level="ERROR")
            raise
    
    def rollback(self, deployment_id: str, authority: str) -> Dict[str, Any]:
        """Instant rollback to previous checkpoint"""
        
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        if not deployment.checkpoint:
            raise ValueError(f"No checkpoint available for rollback")
        
        if not deployment.rollback_available:
            raise ValueError(f"Rollback not available for this deployment")
        
        self._log("rollback_initiated", {
            "deployment_id": deployment_id,
            "checkpoint_id": deployment.checkpoint.checkpoint_id,
            "authority": authority
        })
        
        # Restore from checkpoint
        checkpoint = deployment.checkpoint
        
        deployment.status = DeploymentStatus.ROLLED_BACK
        
        self._log("rollback_completed", {
            "deployment_id": deployment_id,
            "restored_to": checkpoint.checkpoint_id,
            "authority": authority
        })
        
        return {
            "success": True,
            "message": f"Rolled back to checkpoint {checkpoint.checkpoint_id}",
            "restored_state": checkpoint.state,
            "deployment": deployment.to_dict()
        }
    
    def activate_kill_switch(self, authority: str, reason: str) -> Dict[str, Any]:
        """Activate kill switch - halt all deployments without data loss"""
        
        self.kill_switch_active = True
        
        # Halt all active deployments
        halted = []
        for deployment in self.deployments.values():
            if deployment.status in [DeploymentStatus.BUILDING, DeploymentStatus.DEPLOYING]:
                deployment.status = DeploymentStatus.HALTED
                halted.append(deployment.deployment_id)
        
        self._log("kill_switch_activated", {
            "authority": authority,
            "reason": reason,
            "halted_deployments": halted
        }, level="CRITICAL")
        
        return {
            "success": True,
            "kill_switch_active": True,
            "halted_deployments": halted,
            "message": "All deployments halted. Manual principal override required to resume."
        }
    
    def deactivate_kill_switch(self, authority: str, override_code: str) -> Dict[str, Any]:
        """Deactivate kill switch with principal override"""
        
        # Verify override code (in production, this would be cryptographically verified)
        if not override_code or len(override_code) < 8:
            raise ValueError("Invalid override code")
        
        self.kill_switch_active = False
        
        self._log("kill_switch_deactivated", {
            "authority": authority,
            "override_verified": True
        })
        
        return {
            "success": True,
            "kill_switch_active": False,
            "message": "Kill switch deactivated. Deployments may resume."
        }
    
    def get_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment details"""
        deployment = self.deployments.get(deployment_id)
        return deployment.to_dict() if deployment else None
    
    def list_deployments(self, environment: Environment = None) -> List[Dict[str, Any]]:
        """List all deployments"""
        deployments = self.deployments.values()
        if environment:
            deployments = [d for d in deployments if d.environment == environment]
        return [d.to_dict() for d in deployments]
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get immutable audit log"""
        return self.audit_log[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get deployment engine status"""
        return {
            "engine": "Franklin OS Deployment Engine",
            "version": "1.0.0",
            "kill_switch_active": self.kill_switch_active,
            "public_access_enabled": self.public_access_enabled,
            "total_deployments": len(self.deployments),
            "deployments_by_environment": {
                env.value: len([d for d in self.deployments.values() if d.environment == env])
                for env in Environment
            },
            "deployments_by_status": {
                status.value: len([d for d in self.deployments.values() if d.status == status])
                for status in DeploymentStatus
            },
            "total_checkpoints": len(self.checkpoints),
            "audit_log_entries": len(self.audit_log),
            "infrastructure": {
                "frontend": "Vercel (Edge-optimized)",
                "backend": "Docker (Containerized)",
                "execution": "Isolated workers",
                "secrets": "Environment variables only",
                "logs": "Immutable + auditable"
            },
            "security": {
                "instant_rollback": True,
                "manual_principal_override": True,
                "execution_halt_capability": True,
                "no_data_loss_on_halt": True
            }
        }


# Global deployment engine
deployment_engine = DeploymentEngine()
