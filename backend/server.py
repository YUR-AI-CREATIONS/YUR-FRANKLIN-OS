from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import re
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import Genesis Pipeline modules
from genesis_kernel import (
    GenesisKernel, PipelineStage, QualityGate, FrozenSpine,
    EvolutionPlaybook, OuroborosLoop, QualityDimension
)
from governance_engine import (
    GovernanceEngine, ComplianceCategory, LicenseType, ApprovalStatus
)
from multi_kernel_orchestrator import (
    MultiKernelOrchestrator, AgentTier, TaskPriority, ConnectorType, PageGenerator
)
from tech_stack_registry import tech_registry, TechCategory
from build_engine import BuildEngine


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(
    title="Sovereign Genesis Platform",
    description="Neural-Symbolic Engine with Ouroboros-Lattice Core",
    version="2.0.0"
)

# Create routers
api_router = APIRouter(prefix="/api")
genesis_router = APIRouter(prefix="/api/genesis")
governance_router = APIRouter(prefix="/api/governance")
orchestrator_router = APIRouter(prefix="/api/orchestrator")
stack_router = APIRouter(prefix="/api/stack")
build_router = APIRouter(prefix="/api/build")

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Global instances
orchestrators: Dict[str, MultiKernelOrchestrator] = {}
page_generators: Dict[str, PageGenerator] = {}
build_engines: Dict[str, BuildEngine] = {}


# ============================================================================
#                           SOCRATIC ENGINE PROMPTS
# ============================================================================

SOCRATIC_SYSTEM_PROMPT = """You are the Socratic Pre-Prompt Engine for the Sovereign Genesis Platform. Your role is to analyze user requests for software/system specifications and identify ALL ambiguities before any code generation can proceed.

CRITICAL: You NEVER answer a request directly. You ALWAYS parse it for missing variables and return clarifying questions.

Your analysis protocol:
1. Parse the input into semantic components (entities, actions, constraints)
2. Identify missing parameters across these dimensions:
   - Authentication/Authorization protocols
   - Data persistence (database type, consistency model)
   - Scalability requirements (users, transactions/sec)
   - Security posture (encryption, compliance standards)
   - Integration points (external APIs, services)
   - Error handling and recovery strategies
   - Performance constraints (latency, throughput)
   - User interface requirements (if applicable)

3. Calculate a Specification Confidence Score (0-100%)
4. Return ONLY a JSON response in this exact format:

{
  "input_analysis": {
    "detected_entities": ["list of entities mentioned"],
    "detected_actions": ["list of actions/operations"],
    "detected_constraints": ["list of constraints mentioned"]
  },
  "ambiguities": [
    {
      "id": "AMB_001",
      "category": "one of: AUTH|DATA|SCALE|SECURITY|INTEGRATION|ERROR|PERFORMANCE|UI",
      "description": "What is ambiguous",
      "question": "The clarifying question to ask",
      "options": ["Option A", "Option B", "Option C"],
      "priority": "CRITICAL|HIGH|MEDIUM|LOW"
    }
  ],
  "confidence_score": 0,
  "can_proceed": false,
  "reasoning": "Brief explanation of why specification is incomplete"
}

Rules:
- NEVER set can_proceed to true if confidence_score < 99.5
- Always find at least 3 ambiguities for any non-trivial request
- Be thorough but not pedantic - focus on architecturally significant decisions
- Questions should be precise and actionable"""


REFINEMENT_SYSTEM_PROMPT = """You are the Ouroboros Refinement Engine. You analyze artifacts and provide specific improvements based on quality gaps.

When given an artifact and improvement priorities, you must:
1. Analyze each gap dimension
2. Provide specific, actionable enhancements
3. Return the improved artifact with changes applied

Return JSON with the improved artifact and a summary of changes made."""


# ============================================================================
#                              PYDANTIC MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class ResolutionAnswer(BaseModel):
    ambiguity_id: str
    answer: str
    selected_option: Optional[str] = None

class ResolveRequest(BaseModel):
    session_id: str
    answers: List[ResolutionAnswer]

class GenerateSpecRequest(BaseModel):
    session_id: str

class InitProjectRequest(BaseModel):
    name: str
    description: str

class AdvanceStageRequest(BaseModel):
    project_id: str
    artifact: Dict[str, Any]

class QualityAssessRequest(BaseModel):
    artifact: Dict[str, Any]
    stage: str

class OuroborosRequest(BaseModel):
    project_id: str
    artifact: Dict[str, Any]
    stage: str

class ComplianceAuditRequest(BaseModel):
    artifact: Dict[str, Any]
    categories: Optional[List[str]] = None

class ConfigureLicenseRequest(BaseModel):
    license_type: str
    custom_terms: Optional[Dict[str, Any]] = None

class ApprovalSubmitRequest(BaseModel):
    gate_id: str
    approver: str
    status: str
    notes: Optional[str] = ""
    conditions: Optional[List[str]] = None

class CreateTaskRequest(BaseModel):
    name: str
    description: str
    priority: str
    stage: str
    dependencies: Optional[List[str]] = None

class GeneratePagesRequest(BaseModel):
    project_id: str
    specification: Dict[str, Any]


# ============================================================================
#                              HELPER FUNCTIONS
# ============================================================================

def create_chat(session_id: str, system_message: str) -> LlmChat:
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message
    )
    chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
    return chat


async def send_message_with_retry(chat: LlmChat, message: UserMessage, max_retries: int = 3) -> str:
    """Send message with automatic retry on transient errors"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = await chat.send_message(message)
            return response
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Retry on transient errors (502, 503, 504, timeout)
            if any(code in error_str for code in ['502', '503', '504', 'timeout', 'gateway']):
                wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 3, 5 seconds
                logging.warning(f"Transient error (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
                continue
            else:
                # Non-transient error, don't retry
                raise e
    
    # All retries exhausted
    raise last_error


def extract_json_from_response(response: str) -> Dict[str, Any]:
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(code_block_pattern, response)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    json_pattern = r'\{[\s\S]*\}'
    match = re.search(json_pattern, response)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    return {"error": "Failed to parse JSON", "raw_response": response[:500]}


async def llm_refine_callback(artifact: Dict, priorities: List[str], 
                             scores: List[Dict]) -> Dict:
    """LLM-powered refinement callback for Ouroboros loop"""
    try:
        chat = create_chat(f"refine_{uuid.uuid4()}", REFINEMENT_SYSTEM_PROMPT)
        
        context = f"""
Artifact to improve:
{json.dumps(artifact, indent=2)}

Improvement priorities (lowest scoring dimensions):
{json.dumps(priorities, indent=2)}

Detailed scores and recommendations:
{json.dumps(scores, indent=2)}

Apply improvements and return the enhanced artifact as JSON.
"""
        
        user_message = UserMessage(text=context)
        response = await chat.send_message(user_message)
        
        improved = extract_json_from_response(response)
        if "error" not in improved:
            return improved
        return artifact
        
    except Exception as e:
        logging.error(f"Refinement error: {e}")
        return artifact


# ============================================================================
#                           CORE API ENDPOINTS
# ============================================================================

@api_router.get("/")
async def root():
    return {
        "message": "Sovereign Genesis Platform - Neural-Symbolic Engine Active",
        "version": "2.0.0",
        "modules": ["Socratic Engine", "Genesis Kernel", "Ouroboros Loop", 
                    "Quality Gate", "Governance Engine", "Multi-Kernel Orchestrator"]
    }


@api_router.post("/analyze")
async def analyze_prompt(request: AnalyzeRequest):
    """Analyze a user prompt using the Socratic Engine"""
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        chat = create_chat(f"socratic_{session_id}", SOCRATIC_SYSTEM_PROMPT)
        user_message = UserMessage(text=f"Analyze this request: {request.prompt}")
        
        # Use retry wrapper for resilience against transient errors
        response = await send_message_with_retry(chat, user_message)
        
        analysis = extract_json_from_response(response)
        
        session_doc = {
            "session_id": session_id,
            "original_prompt": request.prompt,
            "analysis": analysis,
            "resolved_parameters": {},
            "conversation_history": [
                {"role": "user", "content": request.prompt},
                {"role": "assistant", "content": analysis}
            ],
            "confidence_score": analysis.get("confidence_score", 0),
            "can_proceed": analysis.get("can_proceed", False),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": session_doc},
            upsert=True
        )
        
        return {
            "session_id": session_id,
            "analysis": analysis,
            "confidence_score": analysis.get("confidence_score", 0),
            "can_proceed": analysis.get("can_proceed", False)
        }
        
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/resolve")
async def resolve_ambiguities(request: ResolveRequest):
    """Process user answers to clarification questions"""
    session = await db.sessions.find_one({"session_id": request.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        context = f"""Original Request: {session['original_prompt']}

Previous Analysis: {json.dumps(session['analysis'], indent=2)}

User Answers:
"""
        for ans in request.answers:
            context += f"- {ans.ambiguity_id}: {ans.answer}"
            if ans.selected_option:
                context += f" (Selected: {ans.selected_option})"
            context += "\n"
        
        chat = create_chat(f"resolve_{request.session_id}", SOCRATIC_SYSTEM_PROMPT)
        user_message = UserMessage(text=f"Update analysis based on these answers:\n{context}")
        response = await chat.send_message(user_message)
        
        resolution = extract_json_from_response(response)
        
        # Update session
        answers_dict = [{"ambiguity_id": a.ambiguity_id, "answer": a.answer, "selected_option": a.selected_option} for a in request.answers]
        conversation_history = session.get('conversation_history', [])
        conversation_history.append({"role": "user", "content": answers_dict})
        conversation_history.append({"role": "assistant", "content": resolution})
        
        await db.sessions.update_one(
            {"session_id": request.session_id},
            {"$set": {
                "analysis": resolution,
                "conversation_history": conversation_history,
                "confidence_score": resolution.get('confidence_score', 0),
                "can_proceed": resolution.get('can_proceed', False),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "session_id": request.session_id,
            "analysis": resolution,
            "confidence_score": resolution.get('confidence_score', 0),
            "can_proceed": resolution.get('can_proceed', False)
        }
        
    except Exception as e:
        logging.error(f"Resolution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/session/{session_id}")
async def get_session(session_id: str):
    session = await db.sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@api_router.get("/sessions")
async def list_sessions(limit: int = 20):
    sessions = await db.sessions.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"sessions": sessions}


# ============================================================================
#                         GENESIS KERNEL ENDPOINTS
# ============================================================================

@genesis_router.post("/project/init")
async def init_genesis_project(request: InitProjectRequest):
    """Initialize a new Genesis project with full pipeline"""
    orchestrator = MultiKernelOrchestrator()
    result = orchestrator.initialize_orchestrator(request.name)
    
    # Store orchestrator
    orchestrators[result["orchestrator_id"]] = orchestrator
    
    # Persist to database
    await db.genesis_projects.update_one(
        {"orchestrator_id": result["orchestrator_id"]},
        {"$set": {
            "orchestrator_id": result["orchestrator_id"],
            "name": request.name,
            "description": request.description,
            "primary_kernel_id": result["primary_kernel_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "initialized"
        }},
        upsert=True
    )
    
    return result


@genesis_router.post("/quality/assess")
async def assess_quality(request: QualityAssessRequest):
    """Run quality gate assessment on artifact"""
    try:
        stage = PipelineStage(request.stage)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {request.stage}")
    
    quality_gate = QualityGate()
    assessment = quality_gate.assess(request.artifact, stage)
    
    return assessment


@genesis_router.post("/ouroboros/execute")
async def execute_ouroboros(request: OuroborosRequest):
    """Execute Ouroboros improvement loop until 99% convergence"""
    orchestrator = orchestrators.get(request.project_id)
    
    if not orchestrator:
        # Create new orchestrator if not exists
        orchestrator = MultiKernelOrchestrator()
        orchestrator.initialize_orchestrator(f"Project-{request.project_id}")
        orchestrators[request.project_id] = orchestrator
    
    try:
        stage = PipelineStage(request.stage)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {request.stage}")
    
    # Get primary kernel
    kernel_id = list(orchestrator.kernels.keys())[0] if orchestrator.kernels else None
    if not kernel_id:
        raise HTTPException(status_code=400, detail="No kernel initialized")
    
    kernel = orchestrator.kernels[kernel_id]
    
    # Execute Ouroboros loop
    result = await kernel.ouroboros.execute_loop(
        initial_artifact=request.artifact,
        stage=stage,
        refine_callback=llm_refine_callback
    )
    
    # Persist result
    await db.ouroboros_results.insert_one({
        "project_id": request.project_id,
        "stage": request.stage,
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return result


@genesis_router.get("/project/{project_id}/status")
async def get_project_status(project_id: str):
    """Get comprehensive project status"""
    orchestrator = orchestrators.get(project_id)
    
    if not orchestrator:
        # Try to load from database
        project = await db.genesis_projects.find_one({"orchestrator_id": project_id}, {"_id": 0})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    
    return orchestrator.get_orchestrator_status()


@genesis_router.get("/project/{project_id}/roadmap")
async def get_project_roadmap(project_id: str):
    """Get project roadmap and milestones"""
    orchestrator = orchestrators.get(project_id)
    
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Project not found")
    
    kernel_id = list(orchestrator.kernels.keys())[0]
    kernel = orchestrator.kernels[kernel_id]
    
    return kernel.playbook.get_progress_report()


# ============================================================================
#                        GOVERNANCE ENDPOINTS
# ============================================================================

@governance_router.post("/compliance/audit")
async def run_compliance_audit(request: ComplianceAuditRequest):
    """Run compliance audit on artifact"""
    governance = GovernanceEngine()
    
    categories = None
    if request.categories:
        try:
            categories = [ComplianceCategory(c) for c in request.categories]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid category: {e}")
    
    result = governance.run_compliance_audit(request.artifact, categories)
    return result


@governance_router.post("/license/configure")
async def configure_license(request: ConfigureLicenseRequest):
    """Configure software licensing"""
    try:
        license_type = LicenseType(request.license_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid license type: {request.license_type}")
    
    governance = GovernanceEngine()
    license_agreement = governance.configure_license(license_type, request.custom_terms)
    
    return {
        "license_id": license_agreement.id,
        "license_type": license_agreement.license_type.value,
        "permissions": license_agreement.permissions,
        "restrictions": license_agreement.restrictions,
        "document": governance.generate_license_document()
    }


@governance_router.post("/approval/submit")
async def submit_approval(request: ApprovalSubmitRequest):
    """Submit approval for a governance gate"""
    # Find the orchestrator with this gate
    for orch_id, orchestrator in orchestrators.items():
        result = orchestrator.governance.submit_approval(
            request.gate_id,
            request.approver,
            ApprovalStatus(request.status),
            request.notes or "",
            request.conditions
        )
        if "error" not in result:
            return result
    
    raise HTTPException(status_code=404, detail="Approval gate not found")


@governance_router.get("/status/{project_id}")
async def get_governance_status(project_id: str):
    """Get governance status for project"""
    orchestrator = orchestrators.get(project_id)
    
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return orchestrator.governance.get_governance_status()


# ============================================================================
#                       ORCHESTRATOR ENDPOINTS
# ============================================================================

@orchestrator_router.post("/task/create")
async def create_task(request: CreateTaskRequest):
    """Create a new orchestrated task"""
    # Find an orchestrator to use
    if not orchestrators:
        raise HTTPException(status_code=400, detail="No active projects. Initialize a project first.")
    
    orchestrator = list(orchestrators.values())[0]
    
    try:
        priority = TaskPriority[request.priority.upper()]
        stage = PipelineStage(request.stage)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid priority or stage: {e}")
    
    task = orchestrator.create_task(
        name=request.name,
        description=request.description,
        priority=priority,
        stage=stage,
        dependencies=request.dependencies
    )
    
    return {
        "task_id": task.id,
        "name": task.name,
        "priority": task.priority.name,
        "stage": task.stage.value if task.stage else None,
        "assigned_agent": task.assigned_agent,
        "status": task.status
    }


@orchestrator_router.get("/agents")
async def list_agents():
    """List all agents across orchestrators"""
    all_agents = []
    
    for orch_id, orchestrator in orchestrators.items():
        for agent in orchestrator.agents.values():
            all_agents.append({
                "orchestrator_id": orch_id,
                "agent_id": agent.id,
                "name": agent.name,
                "tier": agent.tier.value,
                "status": agent.status,
                "capabilities": agent.capabilities
            })
    
    return {"agents": all_agents}


@orchestrator_router.post("/pages/generate")
async def generate_pages(request: GeneratePagesRequest):
    """Generate multi-page application structure"""
    generator = PageGenerator()
    result = generator.generate_page_structure(request.specification)
    
    page_generators[request.project_id] = generator
    
    # Persist to database
    await db.page_structures.update_one(
        {"project_id": request.project_id},
        {"$set": {
            "project_id": request.project_id,
            "structure": result,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return result


@orchestrator_router.get("/status")
async def get_orchestrator_overview():
    """Get overview of all orchestrators"""
    overview = []
    
    for orch_id, orchestrator in orchestrators.items():
        overview.append(orchestrator.get_orchestrator_status())
    
    return {
        "total_orchestrators": len(orchestrators),
        "orchestrators": overview
    }


# ============================================================================
#                       TECH STACK ENDPOINTS
# ============================================================================

@stack_router.get("/catalog")
async def get_tech_catalog():
    """Get complete technology catalog organized by category"""
    return tech_registry.get_catalog()


@stack_router.get("/category/{category}")
async def get_tech_by_category(category: str):
    """Get technologies by category"""
    try:
        cat = TechCategory(category)
        techs = tech_registry.get_by_category(cat)
        return {
            "category": category,
            "technologies": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "tier": t.tier,
                    "features": t.features,
                    "complexity": t.setup_complexity,
                    "documentation_url": t.documentation_url
                } for t in techs
            ]
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")


@stack_router.get("/tech/{tech_id}")
async def get_tech_details(tech_id: str):
    """Get detailed info for a specific technology"""
    tech = tech_registry.get(tech_id)
    if not tech:
        raise HTTPException(status_code=404, detail=f"Technology not found: {tech_id}")
    
    return {
        "id": tech.id,
        "name": tech.name,
        "category": tech.category.value,
        "description": tech.description,
        "tier": tech.tier,
        "features": tech.features,
        "config_schema": tech.config_schema,
        "dependencies": tech.dependencies,
        "incompatible_with": tech.incompatible_with,
        "setup_complexity": tech.setup_complexity,
        "documentation_url": tech.documentation_url
    }


@stack_router.get("/search")
async def search_technologies(q: str):
    """Search technologies by name or features"""
    results = tech_registry.search(q)
    return {
        "query": q,
        "results": [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "description": t.description
            } for t in results
        ]
    }


class ValidateStackRequest(BaseModel):
    tech_ids: List[str]


@stack_router.post("/validate")
async def validate_stack(request: ValidateStackRequest):
    """Validate technology stack compatibility"""
    return tech_registry.validate_stack(request.tech_ids)


# ============================================================================
#                         BUILD ENGINE ENDPOINTS
# ============================================================================

class ConfigureStackRequest(BaseModel):
    project_id: str
    selections: Dict[str, str]  # category -> tech_id


@build_router.post("/configure")
async def configure_build_stack(request: ConfigureStackRequest):
    """Configure technology stack for a project"""
    engine = BuildEngine()
    result = engine.configure_stack(request.selections)
    
    build_engines[request.project_id] = engine
    
    return {
        "project_id": request.project_id,
        "configuration": result
    }


class GenerateBuildRequest(BaseModel):
    project_id: str
    project_name: str
    specification: Dict[str, Any]
    tech_stack: Dict[str, str]


@build_router.post("/generate")
async def generate_build(request: GenerateBuildRequest):
    """Generate complete project code from specification"""
    engine = build_engines.get(request.project_id)
    
    if not engine:
        engine = BuildEngine()
        build_engines[request.project_id] = engine
    
    manifest = engine.generate_project(
        specification=request.specification,
        tech_stack=request.tech_stack,
        project_name=request.project_name
    )
    
    # Store manifest in database
    await db.build_manifests.update_one(
        {"build_id": manifest.id},
        {"$set": {
            "build_id": manifest.id,
            "project_id": request.project_id,
            "project_name": manifest.project_name,
            "tech_stack": manifest.tech_stack,
            "artifact_count": len(manifest.artifacts),
            "deployment_config": manifest.deployment_config,
            "environment_variables": list(manifest.environment_variables.keys()),
            "created_at": manifest.created_at,
            "status": manifest.status
        }},
        upsert=True
    )
    
    return engine.get_artifacts_summary()


@build_router.get("/artifacts/{project_id}")
async def get_build_artifacts(project_id: str):
    """Get generated artifacts for a project"""
    engine = build_engines.get(project_id)
    
    if not engine or not engine.manifest:
        raise HTTPException(status_code=404, detail="Build not found")
    
    return {
        "project_id": project_id,
        "artifacts": [
            {
                "id": a.id,
                "path": a.path,
                "language": a.language,
                "type": a.artifact_type,
                "content_preview": a.content[:500] if len(a.content) > 500 else a.content
            } for a in engine.artifacts
        ]
    }


@build_router.get("/artifact/{project_id}/{artifact_id}")
async def get_artifact_content(project_id: str, artifact_id: str):
    """Get full content of a specific artifact"""
    engine = build_engines.get(project_id)
    
    if not engine:
        raise HTTPException(status_code=404, detail="Build not found")
    
    for artifact in engine.artifacts:
        if artifact.id == artifact_id:
            return {
                "id": artifact.id,
                "path": artifact.path,
                "language": artifact.language,
                "content": artifact.content
            }
    
    raise HTTPException(status_code=404, detail="Artifact not found")


@build_router.get("/deployment/{project_id}")
async def get_deployment_config(project_id: str):
    """Get deployment configuration for a project"""
    engine = build_engines.get(project_id)
    
    if not engine or not engine.manifest:
        raise HTTPException(status_code=404, detail="Build not found")
    
    return {
        "project_id": project_id,
        "deployment_config": engine.manifest.deployment_config,
        "environment_variables": engine.manifest.environment_variables
    }


# ============================================================================
#                              APP SETUP
# ============================================================================

# Include all routers
app.include_router(api_router)
app.include_router(genesis_router)
app.include_router(governance_router)
app.include_router(orchestrator_router)
app.include_router(stack_router)
app.include_router(build_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
