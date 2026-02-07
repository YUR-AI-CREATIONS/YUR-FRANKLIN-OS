from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
from llm_providers import (
    HybridLLMProvider, LLMConfig, LLMMode, OllamaProvider,
    RECOMMENDED_MODELS, get_recommended_model
)
import json
import re
import asyncio
import shutil
import zipfile
import io
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
from prompt_optimizer import prompt_optimizer, OPTIMIZATION_SYSTEM_PROMPT
from marketing_generator import marketing_generator, MARKETING_SYSTEM_PROMPT


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
llm_router = APIRouter(prefix="/api/llm")
prompt_router = APIRouter(prefix="/api/prompt")
marketing_router = APIRouter(prefix="/api/marketing")

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Global instances
orchestrators: Dict[str, MultiKernelOrchestrator] = {}
page_generators: Dict[str, PageGenerator] = {}
build_engines: Dict[str, BuildEngine] = {}

# ============================================================================
#                        LLM PROVIDER MANAGEMENT
# ============================================================================

# Global LLM Provider - supports cloud/local switching
llm_provider: Optional[HybridLLMProvider] = None

def get_default_llm_config() -> LLMConfig:
    """Create default LLM configuration"""
    return LLMConfig(
        mode=LLMMode.CLOUD,  # Default to cloud
        cloud_provider="anthropic",
        cloud_model="claude-sonnet-4-5-20250929",
        emergent_key=EMERGENT_LLM_KEY,
        local_url="http://localhost:11434",
        local_model="llama3.1:8b",
        fallback_to_cloud=True,
        max_retries=3
    )

async def initialize_llm_provider():
    """Initialize the global LLM provider"""
    global llm_provider
    config = get_default_llm_config()
    llm_provider = HybridLLMProvider(config)
    await llm_provider.initialize()
    
    # If local is not available and mode is local-only, auto-switch to hybrid
    if not llm_provider.local_available and config.mode == LLMMode.LOCAL:
        logging.warning("Local LLM unavailable, switching to hybrid mode with cloud fallback")
        llm_provider.config.mode = LLMMode.HYBRID
        llm_provider.config.fallback_to_cloud = True
    
    logging.info(f"LLM Provider initialized: mode={llm_provider.config.mode.value}, local_available={llm_provider.local_available}")

async def get_llm_provider() -> HybridLLMProvider:
    """Get the global LLM provider, initializing if needed"""
    global llm_provider
    if llm_provider is None:
        await initialize_llm_provider()
    return llm_provider


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


class LLMConfigRequest(BaseModel):
    mode: Literal["cloud", "local", "hybrid"]
    local_model: Optional[str] = "llama3.1:8b"
    local_url: Optional[str] = "http://localhost:11434"
    fallback_to_cloud: Optional[bool] = True


class LLMTestRequest(BaseModel):
    prompt: str
    prefer_local: Optional[bool] = True


class PromptOptimizeRequest(BaseModel):
    prompt: str
    use_llm: Optional[bool] = True


class MarketingGenerateRequest(BaseModel):
    project_name: str
    specification: Dict[str, Any]
    tech_stack: Optional[Dict[str, str]] = None


class EnhancedBuildRequest(BaseModel):
    project_id: str
    project_name: str
    specification: Dict[str, Any]
    tech_stack: Optional[Dict[str, str]] = None
    include_auth: Optional[bool] = True
    include_tests: Optional[bool] = True
    include_crud: Optional[bool] = True


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


async def generate_with_hybrid_llm(system_prompt: str, user_message: str, 
                                   prefer_local: bool = True) -> Dict[str, Any]:
    """
    Generate response using the hybrid LLM provider.
    Supports automatic switching between cloud and local LLMs.
    
    Returns:
        Dict with 'response', 'provider', 'model', and metadata
    """
    provider = await get_llm_provider()
    result = await provider.generate(
        system_prompt=system_prompt,
        user_message=user_message,
        prefer_local=prefer_local,
        temperature=0.7
    )
    return result


async def llm_refine_callback(artifact: Dict, priorities: List[str], 
                             scores: List[Dict]) -> Dict:
    """LLM-powered refinement callback for Ouroboros loop"""
    try:
        context = f"""
Artifact to improve:
{json.dumps(artifact, indent=2)}

Improvement priorities (lowest scoring dimensions):
{json.dumps(priorities, indent=2)}

Detailed scores and recommendations:
{json.dumps(scores, indent=2)}

Apply improvements and return the enhanced artifact as JSON.
"""
        
        # Use hybrid LLM provider (prefers local for cost savings)
        result = await generate_with_hybrid_llm(
            system_prompt=REFINEMENT_SYSTEM_PROMPT,
            user_message=context,
            prefer_local=True
        )
        
        improved = extract_json_from_response(result["response"])
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
    """Analyze a user prompt using the Socratic Engine with hybrid LLM support"""
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Use hybrid LLM provider (respects cloud/local mode setting)
        result = await generate_with_hybrid_llm(
            system_prompt=SOCRATIC_SYSTEM_PROMPT,
            user_message=f"Analyze this request: {request.prompt}",
            prefer_local=True  # Default to local for cost savings
        )
        
        analysis = extract_json_from_response(result["response"])
        
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
            "llm_provider": result.get("provider", "unknown"),
            "llm_model": result.get("model", "unknown"),
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
            "can_proceed": analysis.get("can_proceed", False),
            "llm_info": {
                "provider": result.get("provider"),
                "model": result.get("model")
            }
        }
        
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/resolve")
async def resolve_ambiguities(request: ResolveRequest):
    """Process user answers to clarification questions using hybrid LLM"""
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
        
        # Use hybrid LLM provider
        result = await generate_with_hybrid_llm(
            system_prompt=SOCRATIC_SYSTEM_PROMPT,
            user_message=f"Update analysis based on these answers:\n{context}",
            prefer_local=True
        )
        
        resolution = extract_json_from_response(result["response"])
        
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
                "llm_provider": result.get("provider", "unknown"),
                "llm_model": result.get("model", "unknown"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "session_id": request.session_id,
            "analysis": resolution,
            "confidence_score": resolution.get('confidence_score', 0),
            "can_proceed": resolution.get('can_proceed', False),
            "llm_info": {
                "provider": result.get("provider"),
                "model": result.get("model")
            }
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
    """Execute Ouroboros improvement loop until target score convergence"""
    # Get or create orchestrator
    orchestrator = orchestrators.get(request.project_id)
    
    if not orchestrator:
        # Create new orchestrator and kernel automatically
        orchestrator = MultiKernelOrchestrator()
        orchestrator.initialize_orchestrator(f"Project-{request.project_id}")
        orchestrators[request.project_id] = orchestrator
    
    try:
        stage = PipelineStage(request.stage)
    except ValueError:
        stage = PipelineStage.SPECIFICATION  # Default to specification stage
    
    # Ensure at least one kernel exists
    if not orchestrator.kernels:
        kernel = GenesisKernel()
        kernel.initialize()
        kernel_id = str(uuid.uuid4())
        orchestrator.kernels[kernel_id] = kernel
    
    # Get primary kernel
    kernel_id = list(orchestrator.kernels.keys())[0]
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
            categories = [ComplianceCategory(c.lower().replace("-", "_")) for c in request.categories]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid category: {e}")
    
    result = governance.run_compliance_audit(request.artifact, categories)
    
    # Add audit_id to result
    audit_id = str(uuid.uuid4())
    result["audit_id"] = audit_id
    
    # Store in database
    await db.compliance_audits.insert_one({
        "audit_id": audit_id,
        **result,
        "artifact": request.artifact,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
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


class WriteToDiskRequest(BaseModel):
    project_id: str
    output_directory: Optional[str] = "/app/generated"


@build_router.post("/write")
async def write_build_to_disk(request: WriteToDiskRequest):
    """
    Write all generated code artifacts to actual files on disk.
    
    This is the critical step that transforms JSON artifacts into real code.
    """
    engine = build_engines.get(request.project_id)
    
    if not engine or not engine.manifest:
        raise HTTPException(status_code=404, detail="Build not found. Run /api/build/generate first.")
    
    # Write files to disk
    result = engine.write_to_disk(request.output_directory)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=f"Failed to write files: {result.get('errors')}")
    
    # Store record in database
    await db.build_writes.insert_one({
        "project_id": request.project_id,
        "build_id": engine.manifest.id,
        "output_directory": result["output_directory"],
        "total_files": result["total_files_written"],
        "files": result["files"],
        "written_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "success": True,
        "message": f"Successfully wrote {result['total_files_written']} files to disk",
        "output_directory": result["output_directory"],
        "project_name": result["project_name"],
        "tech_stack": result["tech_stack"],
        "files": result["files"]
    }


@build_router.get("/tree/{project_id}")
async def get_build_file_tree(project_id: str):
    """Get the file tree structure of generated artifacts"""
    engine = build_engines.get(project_id)
    
    if not engine or not engine.manifest:
        raise HTTPException(status_code=404, detail="Build not found")
    
    return {
        "project_id": project_id,
        "project_name": engine.manifest.project_name,
        "tree": engine.get_file_tree()
    }


# ============================================================================
#                           LLM PROVIDER ENDPOINTS
# ============================================================================

@llm_router.get("/status")
async def get_llm_status():
    """Get current LLM provider status and configuration"""
    provider = await get_llm_provider()
    status = provider.get_status()
    
    return {
        "status": "active",
        "configuration": status,
        "recommended_models": RECOMMENDED_MODELS,
        "instructions": {
            "cloud": "Uses Emergent LLM Key for Claude/GPT access. Costs per request.",
            "local": "Requires Ollama installed locally. Free unlimited usage.",
            "hybrid": "Uses local when available, falls back to cloud.",
            "setup_ollama": "curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3.1:8b"
        }
    }


@llm_router.post("/config")
async def configure_llm(request: LLMConfigRequest):
    """
    Configure LLM provider mode.
    
    Modes:
    - 'cloud': Always use Claude via Emergent Key (costs per request)
    - 'local': Use Ollama (free, requires local setup)
    - 'hybrid': Local with cloud fallback (recommended for development)
    """
    global llm_provider
    
    try:
        mode = LLMMode(request.mode)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}. Use 'cloud', 'local', or 'hybrid'")
    
    # Create new configuration
    config = LLMConfig(
        mode=mode,
        cloud_provider="anthropic",
        cloud_model="claude-sonnet-4-5-20250929",
        emergent_key=EMERGENT_LLM_KEY,
        local_url=request.local_url or "http://localhost:11434",
        local_model=request.local_model or "llama3.1:8b",
        fallback_to_cloud=request.fallback_to_cloud if request.fallback_to_cloud is not None else True,
        max_retries=3
    )
    
    # Reinitialize provider with new config
    llm_provider = HybridLLMProvider(config)
    await llm_provider.initialize()
    
    status = llm_provider.get_status()
    
    return {
        "message": f"LLM provider configured to '{mode.value}' mode",
        "configuration": status,
        "warnings": [] if status["local_available"] or mode == LLMMode.CLOUD else [
            "Local LLM (Ollama) is not available. Will fall back to cloud if enabled.",
            "To set up Ollama: curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3.1:8b"
        ]
    }


@llm_router.get("/models")
async def list_local_models():
    """List available local models (if Ollama is running)"""
    provider = await get_llm_provider()
    
    if not provider.local_available:
        return {
            "available": False,
            "models": [],
            "message": "Ollama is not running. Start it with: ollama serve"
        }
    
    models = await provider.local_provider.list_models()
    
    return {
        "available": True,
        "models": models,
        "recommended": RECOMMENDED_MODELS
    }


@llm_router.post("/test")
async def test_llm(request: LLMTestRequest):
    """Test LLM generation with a simple prompt"""
    try:
        result = await generate_with_hybrid_llm(
            system_prompt="You are a helpful assistant. Keep responses brief.",
            user_message=request.prompt,
            prefer_local=request.prefer_local if request.prefer_local is not None else True
        )
        
        return {
            "success": True,
            "response": result["response"][:500] if len(result["response"]) > 500 else result["response"],
            "provider_used": result["provider"],
            "model_used": result["model"],
            "request_counts": result.get("request_counts", {})
        }
        
    except Exception as e:
        logging.error(f"LLM test error: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check LLM configuration with GET /api/llm/status"
        }


# ============================================================================
#                         PROMPT OPTIMIZATION ENDPOINTS
# ============================================================================

@prompt_router.post("/optimize")
async def optimize_prompt(request: PromptOptimizeRequest):
    """
    Optimize a user prompt for maximum clarity and completeness.
    
    - Quick mode (use_llm=False): Fast pattern matching
    - Full mode (use_llm=True): LLM-powered deep analysis
    """
    # Quick optimization (pattern matching)
    quick_result = prompt_optimizer.quick_optimize(request.prompt)
    
    if not request.use_llm:
        return {
            "mode": "quick",
            "result": quick_result
        }
    
    # Full LLM optimization
    try:
        llm_result = await generate_with_hybrid_llm(
            system_prompt=OPTIMIZATION_SYSTEM_PROMPT,
            user_message=f"Optimize this requirement:\n{request.prompt}",
            prefer_local=True
        )
        
        full_analysis = extract_json_from_response(llm_result["response"])
        
        return {
            "mode": "full",
            "quick_analysis": quick_result,
            "llm_analysis": full_analysis,
            "llm_info": {
                "provider": llm_result.get("provider"),
                "model": llm_result.get("model")
            }
        }
        
    except Exception as e:
        logging.error(f"LLM optimization error: {e}")
        return {
            "mode": "quick_fallback",
            "result": quick_result,
            "llm_error": str(e)
        }


@prompt_router.get("/patterns")
async def get_optimization_patterns():
    """Get available optimization patterns"""
    return {
        "expansion_patterns": list(prompt_optimizer.EXPANSION_PATTERNS.keys()),
        "tech_suggestions": list(prompt_optimizer.TECH_SUGGESTIONS.keys()),
        "default_stack": prompt_optimizer.default_tech_stack
    }


# ============================================================================
#                         MARKETING CONTENT ENDPOINTS
# ============================================================================

@marketing_router.post("/generate")
async def generate_marketing_content(request: MarketingGenerateRequest):
    """
    Generate complete marketing content for a project.
    
    Includes: taglines, headlines, descriptions, landing page HTML,
    email templates, and social media posts.
    """
    try:
        # Build context for LLM
        context = f"""
Project Name: {request.project_name}

Specification:
{json.dumps(request.specification, indent=2)}

Tech Stack: {json.dumps(request.tech_stack or {}, indent=2)}
"""
        
        # Generate content via LLM
        llm_result = await generate_with_hybrid_llm(
            system_prompt=MARKETING_SYSTEM_PROMPT,
            user_message=f"Generate marketing content for:\n{context}",
            prefer_local=False  # Use cloud for better quality
        )
        
        content = extract_json_from_response(llm_result["response"])
        
        # Generate landing page HTML
        landing_html = marketing_generator.generate_landing_page_html(
            content, 
            request.project_name,
            request.tech_stack
        )
        
        # Generate email templates
        emails = marketing_generator.generate_email_templates(content, request.project_name)
        
        # Generate social posts
        social = marketing_generator.generate_social_posts(content, request.project_name)
        
        # Store in database
        marketing_id = str(uuid.uuid4())
        await db.marketing_content.insert_one({
            "id": marketing_id,
            "project_name": request.project_name,
            "content": content,
            "landing_html": landing_html,
            "emails": emails,
            "social_posts": social,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "id": marketing_id,
            "project_name": request.project_name,
            "content": content,
            "landing_page_html": landing_html,
            "email_templates": emails,
            "social_posts": social,
            "llm_info": {
                "provider": llm_result.get("provider"),
                "model": llm_result.get("model")
            }
        }
        
    except Exception as e:
        logging.error(f"Marketing generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@marketing_router.get("/content/{marketing_id}")
async def get_marketing_content(marketing_id: str):
    """Get previously generated marketing content"""
    content = await db.marketing_content.find_one({"id": marketing_id}, {"_id": 0})
    if not content:
        raise HTTPException(status_code=404, detail="Marketing content not found")
    return content


# ============================================================================
#                         ENHANCED BUILD ENDPOINTS
# ============================================================================

@build_router.post("/enhanced")
async def enhanced_build(request: EnhancedBuildRequest):
    """
    Generate a complete project with CRUD, Auth, and Tests.
    
    Features:
    - Full CRUD routes for each entity
    - JWT authentication module
    - Pytest test suite
    - Database migrations
    """
    engine = BuildEngine()
    build_engines[request.project_id] = engine
    
    # Get or create default tech stack
    tech_stack = request.tech_stack or {
        "frontend_framework": "nextjs",
        "backend_framework": "fastapi",
        "database": "postgresql",
        "css_framework": "tailwindcss",
        "ci_cd": "github_actions"
    }
    
    # Generate base project
    manifest = engine.generate_project(
        specification=request.specification,
        tech_stack=tech_stack,
        project_name=request.project_name
    )
    
    # Add enhanced features
    entities = request.specification.get("data_model", {}).get("entities", [])
    
    # Generate CRUD routes for each entity
    if request.include_crud and entities:
        for entity in entities:
            crud_code = engine.generate_crud_routes(
                entity.get("name", "Entity"),
                entity.get("attributes", [])
            )
            engine._add_artifact(
                f"{request.project_name}/backend/app/routes/{entity['name'].lower()}_routes.py",
                crud_code,
                "file", "python"
            )
    
    # Generate auth module
    if request.include_auth:
        auth_files = engine.generate_auth_module(request.project_name)
        for filename, content in auth_files.items():
            engine._add_artifact(
                f"{request.project_name}/backend/app/auth/{filename}",
                content,
                "file", "python"
            )
    
    # Generate test suite
    if request.include_tests and entities:
        for entity in entities:
            test_code = engine.generate_test_suite(
                entity.get("name", "Entity"),
                entity.get("attributes", [])
            )
            engine._add_artifact(
                f"{request.project_name}/backend/tests/test_{entity['name'].lower()}.py",
                test_code,
                "file", "python"
            )
        
        # Add pytest config
        engine._add_artifact(
            f"{request.project_name}/backend/pytest.ini",
            "[pytest]\npythonpath = .\ntestpaths = tests\naddopts = -v --tb=short\n",
            "file", "ini"
        )
        
        # Add test requirements
        engine._add_artifact(
            f"{request.project_name}/backend/requirements-test.txt",
            "pytest>=7.4.0\npytest-asyncio>=0.21.0\nhttpx>=0.25.0\n",
            "file", "text"
        )
    
    return {
        "project_id": request.project_id,
        "build_id": manifest.id,
        "project_name": request.project_name,
        "total_artifacts": len(engine.artifacts),
        "features": {
            "crud": request.include_crud,
            "auth": request.include_auth,
            "tests": request.include_tests
        },
        "artifacts_by_type": engine.get_artifacts_summary().get("artifacts_by_language", {})
    }


@build_router.get("/download/{project_id}")
async def download_project_zip(project_id: str):
    """
    Download the generated project as a ZIP file.
    """
    engine = build_engines.get(project_id)
    
    if not engine or not engine.manifest:
        raise HTTPException(status_code=404, detail="Build not found. Generate a project first.")
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for artifact in engine.artifacts:
            zip_file.writestr(artifact.path, artifact.content)
        
        # Add manifest
        manifest_data = {
            "id": engine.manifest.id,
            "project_name": engine.manifest.project_name,
            "tech_stack": engine.manifest.tech_stack,
            "deployment_config": engine.manifest.deployment_config,
            "environment_variables": engine.manifest.environment_variables,
            "created_at": engine.manifest.created_at,
            "files": [{"path": a.path, "language": a.language} for a in engine.artifacts]
        }
        zip_file.writestr(
            f"{engine.manifest.project_name}/sgp-manifest.json",
            json.dumps(manifest_data, indent=2)
        )
    
    zip_buffer.seek(0)
    
    # Save to temp file for download
    zip_path = Path(f"/tmp/{engine.manifest.project_name}_{project_id[:8]}.zip")
    zip_path.write_bytes(zip_buffer.getvalue())
    
    return FileResponse(
        path=str(zip_path),
        filename=f"{engine.manifest.project_name}.zip",
        media_type="application/zip"
    )


@build_router.get("/preview/{project_id}")
async def get_build_preview(project_id: str):
    """
    Get a preview of all generated files with content snippets.
    """
    engine = build_engines.get(project_id)
    
    if not engine or not engine.manifest:
        raise HTTPException(status_code=404, detail="Build not found")
    
    previews = []
    for artifact in engine.artifacts:
        content_preview = artifact.content[:500] + "..." if len(artifact.content) > 500 else artifact.content
        previews.append({
            "path": artifact.path,
            "language": artifact.language,
            "size": len(artifact.content),
            "preview": content_preview
        })
    
    return {
        "project_id": project_id,
        "project_name": engine.manifest.project_name,
        "total_files": len(previews),
        "files": previews
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
app.include_router(llm_router)
app.include_router(prompt_router)
app.include_router(marketing_router)

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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_llm_provider()
    logger.info("Sovereign Genesis Platform started - LLM Provider initialized")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
