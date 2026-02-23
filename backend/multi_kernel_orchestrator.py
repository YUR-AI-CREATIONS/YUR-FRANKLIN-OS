"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MULTI-KERNEL ORCHESTRATOR                                 ║
║                                                                              ║
║  Coordinates parallel execution of multiple Genesis kernels.                 ║
║  Manages agent tiers, task prioritization, and cross-kernel communication.   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from genesis_kernel import GenesisKernel, PipelineStage, QualityGate, FrozenSpine
from governance_engine import GovernanceEngine, ComplianceCategory, LicenseType


class AgentTier(Enum):
    """Hierarchical agent classification"""
    COMMANDER = "commander"       # Strategic decision-making
    ARCHITECT = "architect"       # System design
    BUILDER = "builder"           # Code generation
    VALIDATOR = "validator"       # Quality assurance
    GUARDIAN = "guardian"         # Security & compliance
    EXECUTOR = "executor"         # Deployment & operations


class TaskPriority(Enum):
    """Task prioritization levels"""
    CRITICAL = 0    # Blocking, immediate
    HIGH = 1        # Important, time-sensitive
    MEDIUM = 2      # Standard priority
    LOW = 3         # Background, deferrable
    BACKLOG = 4     # Future consideration


class ConnectorType(Enum):
    """Integration connector types"""
    DATABASE = "database"
    API = "api"
    MESSAGE_QUEUE = "message_queue"
    FILE_STORAGE = "file_storage"
    AUTHENTICATION = "authentication"
    MONITORING = "monitoring"
    NOTIFICATION = "notification"


@dataclass
class Agent:
    """Genesis Agent definition"""
    id: str
    name: str
    tier: AgentTier
    capabilities: List[str]
    assigned_stages: List[PipelineStage]
    status: str = "idle"  # idle, active, blocked, completed
    current_task: Optional[str] = None
    performance_score: float = 100.0


@dataclass
class Task:
    """Orchestrated task definition"""
    id: str
    name: str
    description: str
    priority: TaskPriority
    assigned_agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    stage: Optional[PipelineStage] = None
    status: str = "queued"  # queued, in_progress, completed, failed, blocked
    result: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Connector:
    """Integration connector definition"""
    id: str
    name: str
    connector_type: ConnectorType
    config: Dict[str, Any]
    status: str = "disconnected"  # disconnected, connected, error
    last_health_check: Optional[str] = None


class MultiKernelOrchestrator:
    """
    The Master Conductor
    
    Orchestrates multiple Genesis kernels, manages agent hierarchies,
    coordinates task execution, and maintains system-wide coherence.
    """
    
    def __init__(self):
        self.kernels: Dict[str, GenesisKernel] = {}
        self.agents: Dict[str, Agent] = {}
        self.tasks: List[Task] = []
        self.connectors: Dict[str, Connector] = {}
        self.governance = GovernanceEngine()
        self.execution_log: List[Dict[str, Any]] = []
        self.orchestrator_id = str(uuid.uuid4())
        
    def initialize_orchestrator(self, project_name: str) -> Dict[str, Any]:
        """Initialize the multi-kernel orchestration system"""
        # Create primary kernel
        primary_kernel = GenesisKernel()
        kernel_init = primary_kernel.initialize_project(project_name, 
            f"Multi-kernel orchestrated project: {project_name}")
        
        kernel_id = kernel_init["project_id"]
        self.kernels[kernel_id] = primary_kernel
        
        # Initialize agent hierarchy
        self._initialize_agents()
        
        # Initialize governance
        stages = [s.value for s in PipelineStage]
        self.governance.create_approval_workflow(stages)
        
        self._log_execution("orchestrator_initialized", {
            "orchestrator_id": self.orchestrator_id,
            "primary_kernel": kernel_id,
            "agents_count": len(self.agents)
        })
        
        return {
            "orchestrator_id": self.orchestrator_id,
            "primary_kernel_id": kernel_id,
            "agents": [{
                "id": a.id,
                "name": a.name,
                "tier": a.tier.value
            } for a in self.agents.values()],
            "status": "initialized"
        }
    
    def _initialize_agents(self):
        """Create the agent hierarchy"""
        agent_configs = [
            {
                "name": "Strategic Commander",
                "tier": AgentTier.COMMANDER,
                "capabilities": ["strategic_planning", "resource_allocation", "decision_making"],
                "stages": [PipelineStage.INCEPTION, PipelineStage.GOVERNANCE]
            },
            {
                "name": "System Architect",
                "tier": AgentTier.ARCHITECT,
                "capabilities": ["system_design", "component_modeling", "interface_definition"],
                "stages": [PipelineStage.SPECIFICATION, PipelineStage.ARCHITECTURE]
            },
            {
                "name": "Code Builder",
                "tier": AgentTier.BUILDER,
                "capabilities": ["code_generation", "testing", "documentation"],
                "stages": [PipelineStage.CONSTRUCTION]
            },
            {
                "name": "Quality Validator",
                "tier": AgentTier.VALIDATOR,
                "capabilities": ["quality_assessment", "testing", "performance_analysis"],
                "stages": [PipelineStage.VALIDATION, PipelineStage.EVOLUTION]
            },
            {
                "name": "Security Guardian",
                "tier": AgentTier.GUARDIAN,
                "capabilities": ["security_audit", "compliance_check", "vulnerability_scan"],
                "stages": [PipelineStage.VALIDATION, PipelineStage.GOVERNANCE]
            },
            {
                "name": "Deployment Executor",
                "tier": AgentTier.EXECUTOR,
                "capabilities": ["deployment", "monitoring", "incident_response"],
                "stages": [PipelineStage.DEPLOYMENT]
            }
        ]
        
        for config in agent_configs:
            agent = Agent(
                id=str(uuid.uuid4()),
                name=config["name"],
                tier=config["tier"],
                capabilities=config["capabilities"],
                assigned_stages=config["stages"]
            )
            self.agents[agent.id] = agent
    
    def create_task(self, name: str, description: str, 
                   priority: TaskPriority, stage: PipelineStage,
                   dependencies: List[str] = None) -> Task:
        """Create and queue a new task"""
        task = Task(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            priority=priority,
            stage=stage,
            dependencies=dependencies or []
        )
        
        # Auto-assign agent based on stage
        for agent in self.agents.values():
            if stage in agent.assigned_stages and agent.status == "idle":
                task.assigned_agent = agent.id
                agent.status = "assigned"
                agent.current_task = task.id
                break
        
        self.tasks.append(task)
        self._sort_tasks()
        
        self._log_execution("task_created", {
            "task_id": task.id,
            "name": name,
            "priority": priority.value,
            "assigned_agent": task.assigned_agent
        })
        
        return task
    
    def _sort_tasks(self):
        """Sort tasks by priority"""
        self.tasks.sort(key=lambda t: (t.priority.value, t.created_at))
    
    async def execute_task(self, task_id: str, 
                          executor: Callable[[Task], Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a specific task"""
        task = self._find_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # Check dependencies
        unmet = self._check_dependencies(task)
        if unmet:
            task.status = "blocked"
            return {
                "status": "blocked",
                "task_id": task_id,
                "unmet_dependencies": unmet
            }
        
        task.status = "in_progress"
        task.started_at = datetime.now(timezone.utc).isoformat()
        
        # Update agent status
        if task.assigned_agent:
            agent = self.agents.get(task.assigned_agent)
            if agent:
                agent.status = "active"
        
        try:
            result = await executor(task)
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now(timezone.utc).isoformat()
            
            # Update agent
            if task.assigned_agent:
                agent = self.agents.get(task.assigned_agent)
                if agent:
                    agent.status = "idle"
                    agent.current_task = None
            
            self._log_execution("task_completed", {
                "task_id": task_id,
                "result_summary": str(result)[:200]
            })
            
            return {
                "status": "completed",
                "task_id": task_id,
                "result": result
            }
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            
            self._log_execution("task_failed", {
                "task_id": task_id,
                "error": str(e)
            })
            
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(e)
            }
    
    def _check_dependencies(self, task: Task) -> List[str]:
        """Check if task dependencies are met"""
        unmet = []
        for dep_id in task.dependencies:
            dep_task = self._find_task(dep_id)
            if not dep_task or dep_task.status != "completed":
                unmet.append(dep_id)
        return unmet
    
    def _find_task(self, task_id: str) -> Optional[Task]:
        """Find task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def register_connector(self, name: str, connector_type: ConnectorType,
                          config: Dict[str, Any]) -> Connector:
        """Register an integration connector"""
        connector = Connector(
            id=str(uuid.uuid4()),
            name=name,
            connector_type=connector_type,
            config=config
        )
        self.connectors[connector.id] = connector
        
        self._log_execution("connector_registered", {
            "connector_id": connector.id,
            "type": connector_type.value
        })
        
        return connector
    
    async def health_check_connectors(self) -> Dict[str, Any]:
        """Perform health check on all connectors"""
        results = []
        
        for connector in self.connectors.values():
            # Simulated health check - in production would ping actual services
            connector.status = "connected"  # Would be actual check
            connector.last_health_check = datetime.now(timezone.utc).isoformat()
            
            results.append({
                "id": connector.id,
                "name": connector.name,
                "type": connector.connector_type.value,
                "status": connector.status
            })
        
        healthy = sum(1 for r in results if r["status"] == "connected")
        
        return {
            "total_connectors": len(results),
            "healthy": healthy,
            "unhealthy": len(results) - healthy,
            "connectors": results
        }
    
    async def run_pipeline(self, kernel_id: str, 
                          specification: Dict[str, Any],
                          refine_callback: Callable) -> Dict[str, Any]:
        """Execute complete Genesis pipeline for a kernel"""
        kernel = self.kernels.get(kernel_id)
        if not kernel:
            return {"error": f"Kernel {kernel_id} not found"}
        
        pipeline_results = []
        
        # Execute each stage
        for stage in PipelineStage:
            # Create task for stage
            task = self.create_task(
                name=f"Execute {stage.value}",
                description=f"Pipeline stage: {stage.value}",
                priority=TaskPriority.HIGH,
                stage=stage
            )
            
            # Execute with Ouroboros loop
            stage_result = await kernel.ouroboros.execute_loop(
                initial_artifact=specification,
                stage=stage,
                refine_callback=refine_callback
            )
            
            pipeline_results.append({
                "stage": stage.value,
                "status": stage_result["status"],
                "score": stage_result["final_score"],
                "iterations": stage_result["iterations"]
            })
            
            # Check for failure or drift
            if stage_result["status"] in ["DRIFT_ALERT", "MAX_ITERATIONS"]:
                if stage_result["final_score"] < 90:
                    return {
                        "pipeline_status": "HALTED",
                        "halted_at_stage": stage.value,
                        "reason": stage_result["status"],
                        "final_score": stage_result["final_score"],
                        "results": pipeline_results
                    }
            
            # Update specification for next stage
            specification = stage_result["artifact"]
        
        return {
            "pipeline_status": "COMPLETED",
            "results": pipeline_results,
            "final_artifact": specification,
            "governance_status": self.governance.get_governance_status()
        }
    
    def _log_execution(self, event: str, details: Dict[str, Any]):
        """Log orchestration event"""
        self.execution_log.append({
            "event": event,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        active_agents = sum(1 for a in self.agents.values() if a.status == "active")
        pending_tasks = sum(1 for t in self.tasks if t.status in ["queued", "in_progress"])
        completed_tasks = sum(1 for t in self.tasks if t.status == "completed")
        
        return {
            "orchestrator_id": self.orchestrator_id,
            "kernels": {
                "count": len(self.kernels),
                "ids": list(self.kernels.keys())
            },
            "agents": {
                "total": len(self.agents),
                "active": active_agents,
                "by_tier": {
                    tier.value: sum(1 for a in self.agents.values() if a.tier == tier)
                    for tier in AgentTier
                }
            },
            "tasks": {
                "total": len(self.tasks),
                "pending": pending_tasks,
                "completed": completed_tasks,
                "by_priority": {
                    p.name: sum(1 for t in self.tasks if t.priority == p)
                    for p in TaskPriority
                }
            },
            "connectors": {
                "total": len(self.connectors),
                "connected": sum(1 for c in self.connectors.values() if c.status == "connected")
            },
            "governance": self.governance.get_governance_status(),
            "execution_log_entries": len(self.execution_log)
        }


class PageGenerator:
    """
    Multi-Page Application Generator
    
    Generates structured multi-page applications from specifications:
    - Landing Page
    - Application Pages
    - Marketing Content
    - Governance Documentation
    """
    
    def __init__(self):
        self.pages: Dict[str, Dict[str, Any]] = {}
        
    def generate_page_structure(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete page structure from specification"""
        
        self.pages = {
            "landing": self._generate_landing_page(specification),
            "application": self._generate_application_pages(specification),
            "marketing": self._generate_marketing_pages(specification),
            "governance": self._generate_governance_pages(specification)
        }
        
        return {
            "total_pages": sum(len(p.get("pages", [])) for p in self.pages.values()) + len(self.pages),
            "structure": self.pages
        }
    
    def _generate_landing_page(self, spec: Dict) -> Dict[str, Any]:
        """Generate landing page structure"""
        return {
            "type": "landing",
            "route": "/",
            "sections": [
                {
                    "id": "hero",
                    "component": "HeroSection",
                    "content": {
                        "headline": spec.get("name", "Product Name"),
                        "subheadline": spec.get("description", "Product description"),
                        "cta_primary": "Get Started",
                        "cta_secondary": "Learn More"
                    }
                },
                {
                    "id": "features",
                    "component": "FeaturesGrid",
                    "content": {
                        "features": spec.get("features", [])
                    }
                },
                {
                    "id": "social_proof",
                    "component": "Testimonials",
                    "content": {"testimonials": []}
                },
                {
                    "id": "pricing",
                    "component": "PricingTable",
                    "content": {"plans": []}
                },
                {
                    "id": "cta_final",
                    "component": "CTASection",
                    "content": {"headline": "Ready to start?", "cta": "Sign Up Now"}
                }
            ]
        }
    
    def _generate_application_pages(self, spec: Dict) -> Dict[str, Any]:
        """Generate application page structures"""
        components = spec.get("components", [])
        
        pages = [
            {
                "route": "/dashboard",
                "name": "Dashboard",
                "component": "DashboardPage",
                "requires_auth": True
            },
            {
                "route": "/settings",
                "name": "Settings",
                "component": "SettingsPage",
                "requires_auth": True
            }
        ]
        
        # Generate pages from components
        for comp in components:
            if isinstance(comp, dict):
                pages.append({
                    "route": f"/{comp.get('name', 'page').lower().replace(' ', '-')}",
                    "name": comp.get("name", "Page"),
                    "component": f"{comp.get('name', 'Page').replace(' ', '')}Page",
                    "requires_auth": True
                })
        
        return {
            "type": "application",
            "pages": pages
        }
    
    def _generate_marketing_pages(self, spec: Dict) -> Dict[str, Any]:
        """Generate marketing page structures"""
        return {
            "type": "marketing",
            "pages": [
                {
                    "route": "/about",
                    "name": "About Us",
                    "component": "AboutPage",
                    "sections": ["story", "team", "mission", "values"]
                },
                {
                    "route": "/blog",
                    "name": "Blog",
                    "component": "BlogPage",
                    "sections": ["featured", "recent", "categories"]
                },
                {
                    "route": "/contact",
                    "name": "Contact",
                    "component": "ContactPage",
                    "sections": ["form", "info", "map"]
                },
                {
                    "route": "/docs",
                    "name": "Documentation",
                    "component": "DocsPage",
                    "sections": ["getting_started", "api_reference", "guides"]
                }
            ]
        }
    
    def _generate_governance_pages(self, spec: Dict) -> Dict[str, Any]:
        """Generate governance/legal page structures"""
        return {
            "type": "governance",
            "pages": [
                {
                    "route": "/terms",
                    "name": "Terms of Service",
                    "component": "TermsPage",
                    "legal": True
                },
                {
                    "route": "/privacy",
                    "name": "Privacy Policy",
                    "component": "PrivacyPage",
                    "legal": True
                },
                {
                    "route": "/license",
                    "name": "License Agreement",
                    "component": "LicensePage",
                    "legal": True
                },
                {
                    "route": "/compliance",
                    "name": "Compliance",
                    "component": "CompliancePage",
                    "legal": True
                }
            ]
        }
