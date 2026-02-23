"""
FRANKLIN OS API Routes
Integrates all FRANKLIN OS systems: Runtime, Academy, Bot Tiers, Marketplace, Grok Agent, Orchestrator
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx

# Import FRANKLIN OS systems
from franklin_runtime import franklin_runtime, SentinelStatus
from agent_academy import agent_academy
from bot_tiers import bot_tier_system, BotTier
from agent_marketplace import agent_marketplace
from grok_agent import grok_agent
from franklin_orchestrator import franklin_orchestrator
from agent_governance import agent_governance

# Create routers
franklin_router = APIRouter(prefix="/api/franklin")
academy_router = APIRouter(prefix="/api/academy")
bots_router = APIRouter(prefix="/api/bots")
marketplace_router = APIRouter(prefix="/api/marketplace")
grok_router = APIRouter(prefix="/api/grok")
build_orchestrator_router = APIRouter(prefix="/api/build-orchestrator")
persistence_router = APIRouter(prefix="/api/persistence")
tasks_router = APIRouter(prefix="/api/tasks")


# ============================================================================
#                         PYDANTIC MODELS
# ============================================================================

class CreateAgentRequest(BaseModel):
    name: str
    specialization: str
    tier: int = 1
    bio: str = ""


class AuthorizationCheckRequest(BaseModel):
    action: str
    value_usd: float = 0


class SentinelActionRequest(BaseModel):
    action: str  # "quarantine", "revoke", "restore"
    reason: str = ""
    authority: str = ""


class EnrollAgentRequest(BaseModel):
    agent_id: str
    agent_name: str
    program_id: str
    skills: List[str] = []


class CertifyAgentRequest(BaseModel):
    agent_id: str
    agent_name: str
    program_id: str
    ethical_score: float = 100.0
    reliability_score: float = 100.0


class CreateBotRequest(BaseModel):
    name: str
    tier: int  # 1-4


class AssignTaskRequest(BaseModel):
    bot_id: str
    task: Dict[str, Any]


class CompleteTaskRequest(BaseModel):
    bot_id: str
    result: Dict[str, Any]


class GenesisRequest(BaseModel):
    mission: str
    target_file: Optional[str] = None


class DeployAgentRequest(BaseModel):
    agent_id: str
    user_id: str
    deployment_config: Dict[str, Any] = {}


class PurchaseAgentRequest(BaseModel):
    agent_id: str
    user_id: str
    purchase_type: str  # "purchase" or "rental"
    duration_hours: Optional[int] = None


class AutonomousExecutionRequest(BaseModel):
    agent_id: str
    task_description: str
    execution_context: Dict[str, Any] = {}


# ============================================================================
#                         FRANKLIN RUNTIME ROUTES
# ============================================================================

@franklin_router.get("/status")
async def get_franklin_status():
    """Get FRANKLIN runtime status"""
    return franklin_runtime.get_runtime_status()


@franklin_router.get("/dpoa")
async def get_dpoa():
    """Get the DPOA manifest"""
    return franklin_runtime.dpoa


@franklin_router.post("/agent/create")
async def create_franklin_agent(request: CreateAgentRequest):
    """Create a new agent in the Franklin ecosystem"""
    agent = franklin_runtime.create_agent(
        name=request.name,
        specialization=request.specialization,
        tier=request.tier,
        bio=request.bio
    )
    return {
        "success": True,
        "agent": agent.to_dict()
    }


@franklin_router.get("/agents")
async def list_franklin_agents():
    """List all Franklin agents"""
    return {"agents": franklin_runtime.list_agents()}


@franklin_router.get("/agent/{agent_id}")
async def get_franklin_agent(agent_id: str):
    """Get a specific Franklin agent"""
    agent = franklin_runtime.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()


@franklin_router.post("/authorize")
async def check_authorization(request: AuthorizationCheckRequest):
    """Check if an action is authorized under DPOA"""
    return franklin_runtime.check_authorization(request.action, request.value_usd)


@franklin_router.post("/sentinel")
async def sentinel_action(request: SentinelActionRequest):
    """Perform sentinel action (quarantine, revoke, restore)"""
    if request.action == "quarantine":
        return franklin_runtime.sentinel.trigger_quarantine(request.reason)
    elif request.action == "revoke":
        return franklin_runtime.sentinel.revoke(request.authority)
    elif request.action == "restore":
        return franklin_runtime.sentinel.restore(request.authority)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")


@franklin_router.get("/sentinel/status")
async def get_sentinel_status():
    """Get sentinel status"""
    return franklin_runtime.sentinel.check_health()


@franklin_router.get("/pqc/status")
async def get_pqc_status():
    """Get PQC vault status"""
    return franklin_runtime.pqc.get_status()


@franklin_router.post("/pqc/rotate")
async def rotate_pqc_keys():
    """Rotate PQC session keys"""
    franklin_runtime.pqc.rotate()
    return {
        "success": True,
        "message": "Session keys rotated",
        "status": franklin_runtime.pqc.get_status()
    }


@franklin_router.get("/audit")
async def get_audit_log(limit: int = 100):
    """Get audit log entries"""
    return {
        "entries": franklin_runtime.audit.get_entries(limit),
        "merkle_root": franklin_runtime.audit.root_hash,
        "integrity": franklin_runtime.audit.verify_integrity()
    }


# ============================================================================
#                         ACADEMY ROUTES
# ============================================================================

@academy_router.get("/status")
async def get_academy_status():
    """Get academy status"""
    return agent_academy.get_academy_status()


@academy_router.get("/programs")
async def get_programs():
    """Get all training programs"""
    return {"programs": agent_academy.get_programs()}


@academy_router.get("/program/{program_id}")
async def get_program(program_id: str):
    """Get a specific program"""
    program = agent_academy.get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@academy_router.get("/board")
async def get_oversight_board():
    """Get the Human-AI Oversight Board"""
    return {"board": agent_academy.get_oversight_board()}


@academy_router.post("/enroll")
async def enroll_agent(request: EnrollAgentRequest):
    """Enroll an agent in a training program"""
    result = agent_academy.enroll_agent(
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        program_id=request.program_id,
        skills=request.skills
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@academy_router.get("/enrollments")
async def get_enrollments(agent_id: str = None):
    """Get enrollments"""
    return {"enrollments": agent_academy.get_enrollments(agent_id)}


@academy_router.post("/certify")
async def certify_agent_governed(request: CertifyAgentRequest):
    """Certify an agent after program completion with governance verification"""
    # First verify through governance
    governance_result = await agent_governance.verify_certification_request(
        request.agent_id,
        request.program_id,
        request.ethical_score,
        request.reliability_score
    )

    if not governance_result["approved"]:
        raise HTTPException(
            status_code=403,
            detail=f"Certification blocked by governance: {governance_result['message']}"
        )

    # If approved, proceed with certification
    result = agent_academy.certify_agent(
        request.agent_id,
        request.agent_name,
        request.program_id,
        ethical_score=request.ethical_score,
        reliability_score=request.reliability_score
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {
        "success": True,
        "certification": result,
        "governance_checkpoint": governance_result["checkpoint_id"],
        "drift_score": governance_result["drift_score"],
        "requires_board_review": governance_result["requires_board_review"]
    }


@academy_router.get("/certifications")
async def get_certifications(agent_id: str = None):
    """Get issued certifications"""
    return {"certifications": agent_academy.get_certifications(agent_id)}


# ============================================================================
#                         BOT TIER ROUTES
# ============================================================================

@bots_router.get("/status")
async def get_bot_system_status():
    """Get bot system status"""
    return bot_tier_system.get_system_status()


@bots_router.get("/tiers")
async def get_tier_configs():
    """Get all tier configurations"""
    return {"tiers": bot_tier_system.get_tier_configs()}


@bots_router.get("/tier/{tier_level}")
async def get_tier_config(tier_level: int):
    """Get configuration for a specific tier"""
    try:
        tier = BotTier(tier_level)
        return bot_tier_system.get_tier_config(tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier level: {tier_level}")


@bots_router.post("/create")
async def create_bot(request: CreateBotRequest):
    """Create a new bot instance"""
    try:
        tier = BotTier(request.tier)
        bot = bot_tier_system.create_bot(request.name, tier)
        return {
            "success": True,
            "bot": bot.to_dict()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {request.tier}")


@bots_router.get("/list")
async def list_bots(tier: int = None):
    """List all bots"""
    tier_enum = BotTier(tier) if tier else None
    return {"bots": bot_tier_system.list_bots(tier_enum)}


@bots_router.get("/bot/{bot_id}")
async def get_bot(bot_id: str):
    """Get a specific bot"""
    bot = bot_tier_system.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot.to_dict()


@bots_router.post("/task/assign")
async def assign_task(request: AssignTaskRequest):
    """Assign a task to a bot"""
    result = bot_tier_system.assign_task(request.bot_id, request.task)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@bots_router.post("/task/complete")
async def complete_task(request: CompleteTaskRequest):
    """Mark a task as completed"""
    result = bot_tier_system.complete_task(request.bot_id, request.result)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ============================================================================
#                         MARKETPLACE ROUTES
# ============================================================================

@marketplace_router.get("/agents")
async def get_marketplace_agents():
    """Get all marketplace agents"""
    return {"agents": agent_marketplace.get_all_agents()}


@marketplace_router.get("/agents/summary")
async def get_agent_summaries():
    """Get summary view of all agents"""
    return {"agents": agent_marketplace.get_agent_summaries()}


@marketplace_router.get("/agent/{agent_id}")
async def get_marketplace_agent(agent_id: str):
    """Get a specific marketplace agent"""
    agent = agent_marketplace.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@marketplace_router.get("/search")
async def search_agents(specialization: str = None, max_price: float = None):
    """Search agents by criteria"""
    return {"agents": agent_marketplace.search_agents(specialization, max_price)}


@marketplace_router.get("/comparison")
async def get_agent_comparison():
    """Get comparison data for all agents"""
    return agent_marketplace.get_comparison()


@marketplace_router.post("/deploy")
async def deploy_agent_governed(request: DeployAgentRequest):
    """Deploy an agent with governance verification"""
    # First verify through governance
    governance_result = await agent_governance.verify_agent_deployment(
        request.agent_id,
        request.user_id,
        request.deployment_config
    )

    if not governance_result["approved"]:
        raise HTTPException(
            status_code=403,
            detail=f"Deployment blocked by governance: {governance_result['message']}"
        )

    # If approved, proceed with deployment
    deployment_result = agent_marketplace.deploy_agent(
        request.agent_id,
        request.user_id,
        request.deployment_config
    )

    return {
        "success": True,
        "deployment": deployment_result,
        "governance_checkpoint": governance_result["checkpoint_id"],
        "drift_score": governance_result["drift_score"]
    }


@marketplace_router.post("/purchase")
async def purchase_agent_governed(request: PurchaseAgentRequest):
    """Purchase or rent an agent with governance verification"""
    # Verify through governance
    governance_result = await agent_governance.verify_agent_purchase(
        request.agent_id,
        request.user_id,
        request.purchase_type,
        request.duration_hours
    )

    if not governance_result["approved"]:
        raise HTTPException(
            status_code=403,
            detail=f"Purchase blocked by governance: {governance_result['message']}"
        )

    # If approved, proceed with purchase/rental
    if request.purchase_type == "purchase":
        result = agent_marketplace.purchase_agent(request.agent_id, request.user_id)
    else:
        result = agent_marketplace.rent_agent(request.agent_id, request.user_id, request.duration_hours)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {
        "success": True,
        "transaction": result,
        "governance_checkpoint": governance_result["checkpoint_id"],
        "drift_score": governance_result["drift_score"]
    }


@marketplace_router.post("/autonomous/execute")
async def execute_agent_autonomously(request: AutonomousExecutionRequest):
    """Execute agent autonomously with Trinity Spine governance"""
    # Verify through governance with strict checks
    governance_result = await agent_governance.verify_autonomous_execution(
        request.agent_id,
        request.task_description,
        request.execution_context
    )

    if not governance_result["approved"]:
        raise HTTPException(
            status_code=403,
            detail=f"Autonomous execution blocked: {governance_result['message']}"
        )

    # If approved, proceed with autonomous execution
    execution_result = await agent_marketplace.execute_autonomous_task(
        request.agent_id,
        request.task_description,
        request.execution_context
    )

    return {
        "success": True,
        "execution": execution_result,
        "governance_checkpoint": governance_result["checkpoint_id"],
        "safety_score": governance_result["safety_score"],
        "drift_score": governance_result["drift_score"]
    }


@marketplace_router.get("/governance/status")
async def get_governance_status(agent_id: str = None):
    """Get governance status for agents or system"""
    return await agent_governance.get_governance_status(agent_id)


@marketplace_router.get("/governance/checkpoints")
async def get_governance_checkpoints(agent_id: str = None, limit: int = 50):
    """Get governance checkpoints"""
    checkpoints = agent_governance.checkpoints
    if agent_id:
        checkpoints = [c for c in checkpoints if c.agent_id == agent_id]

    # Return most recent checkpoints
    recent_checkpoints = sorted(checkpoints, key=lambda c: c.timestamp, reverse=True)[:limit]

    return {
        "checkpoints": [
            {
                "checkpoint_id": c.checkpoint_id,
                "action": c.action.value,
                "agent_id": c.agent_id,
                "user_id": c.user_id,
                "verified": c.verified,
                "drift_score": c.drift_score,
                "timestamp": c.timestamp
            }
            for c in recent_checkpoints
        ],
        "total": len(checkpoints)
    }


# ============================================================================
#                         GROK AGENT ROUTES
# ============================================================================

@grok_router.get("/status")
async def get_grok_status():
    """Get Grok agent status"""
    return grok_agent.get_status()


@grok_router.post("/genesis")
async def run_genesis_loop(request: GenesisRequest):
    """Run the Genesis self-healing loop"""
    if not grok_agent.is_configured():
        raise HTTPException(status_code=400, detail="Grok API not configured. Set XAI_API_KEY in environment.")
    
    task = await grok_agent.genesis_loop(request.mission, request.target_file)
    return {
        "success": task.status == "completed",
        "task": task.to_dict(),
        "output": grok_agent.get_output_buffer()
    }


@grok_router.get("/tasks")
async def list_grok_tasks():
    """List all Grok tasks"""
    return {"tasks": grok_agent.list_tasks()}


@grok_router.get("/task/{task_id}")
async def get_grok_task(task_id: str):
    """Get a specific Grok task"""
    task = grok_agent.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@grok_router.get("/output")
async def get_grok_output():
    """Get the output buffer (for streaming)"""
    return {"output": grok_agent.get_output_buffer()}


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None


class AgentChatRequest(BaseModel):
    message: str
    context: str
    history: Optional[List[Dict[str, str]]] = None


@grok_router.post("/chat")
async def grok_chat(request: ChatRequest):
    """Have a conversation with Grok/Franklin"""
    response = await grok_agent.chat(request.message, request.history)
    
    if response:
        return {"response": response, "success": True}
    else:
        # Fallback response when Grok is not available
        return {
            "response": f"I received your message: '{request.message}'. I'm here to help you build software. Try using /genesis <description> to start building, or /help for available commands.",
            "success": True,
            "fallback": True
        }


# Agent-specific chat endpoint
agent_chat_router = APIRouter(prefix="/api/agent")

@agent_chat_router.post("/chat")
async def agent_specific_chat(request: AgentChatRequest):
    """Have a conversation with a specific agent/bot/program persona"""
    if not grok_agent.api_key:
        # Return a contextual fallback
        return {"response": "I understand. Tell me more about what you need.", "success": True, "fallback": True}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            messages = [{"role": "system", "content": request.context}]
            
            if request.history:
                for msg in request.history[-6:]:
                    role = "assistant" if msg.get("role") != "user" else "user"
                    messages.append({"role": role, "content": msg.get("content", "")})
            
            messages.append({"role": "user", "content": request.message})
            
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {grok_agent.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            )
            response.raise_for_status()
            result = response.json()
            return {"response": result["choices"][0]["message"]["content"], "success": True}
    except Exception as e:
        return {"response": "Let me think about that... What specifically would you like to explore?", "success": True, "fallback": True}


# ============================================================================
#                         COMBINED DASHBOARD
# ============================================================================

@franklin_router.get("/dashboard")
async def get_franklin_dashboard():
    """Get combined FRANKLIN OS dashboard data"""
    return {
        "runtime": franklin_runtime.get_runtime_status(),
        "academy": agent_academy.get_academy_status(),
        "bots": bot_tier_system.get_system_status(),
        "marketplace": {
            "total_agents": len(agent_marketplace.agents),
            "agents": agent_marketplace.get_agent_summaries()
        },
        "grok": grok_agent.get_status(),
        "timestamp": datetime.utcnow().isoformat()
    }



# ============================================================================
#                         ORCHESTRATOR ROUTES
#                    USER → FRANKLIN → GROK → AGENTS → WORKSPACE
# ============================================================================

class OrchestratorChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class BuildRequest(BaseModel):
    mission: str
    session_id: Optional[str] = None


class AgentInteractRequest(BaseModel):
    agent_role: str  # genesis, architect, implementer, healer
    message: str
    session_id: Optional[str] = None


class ApproveSectionRequest(BaseModel):
    section_id: str
    session_id: Optional[str] = None


@build_orchestrator_router.post("/chat")
async def orchestrator_chat(request: OrchestratorChatRequest):
    """
    Main entry point: User talks to Franklin.
    Franklin perfect-prompts Grok and coordinates agents.
    """
    result = await franklin_orchestrator.franklin_chat(
        request.message,
        request.session_id
    )
    return result


@build_orchestrator_router.post("/build")
async def orchestrator_build(request: BuildRequest):
    """
    Initiate a full build with all agents.
    Genesis → Architect → Implementer → Healer → Governance
    """
    result = await franklin_orchestrator.initiate_build(
        request.mission,
        request.session_id
    )
    return result


@build_orchestrator_router.post("/agent/interact")
async def agent_interact(request: AgentInteractRequest):
    """Interact with a specific Genesis agent"""
    result = await franklin_orchestrator.agent_interact(
        request.agent_role,
        request.message,
        request.session_id
    )
    return result


@build_orchestrator_router.get("/whiteboard")
async def get_whiteboard(session_id: Optional[str] = None):
    """Get the current whiteboard - all sections for collaborative review"""
    return franklin_orchestrator.get_whiteboard(session_id)


@build_orchestrator_router.post("/approve")
async def approve_section(request: ApproveSectionRequest):
    """User approves a whiteboard section"""
    return franklin_orchestrator.approve_section(
        request.section_id,
        request.session_id
    )


@build_orchestrator_router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get a specific build session"""
    session = franklin_orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return franklin_orchestrator.get_whiteboard(session_id)


@build_orchestrator_router.get("/sessions")
async def list_sessions():
    """List all build sessions"""
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "mission": s.mission,
                "status": s.status,
                "phase": s.current_phase.value,
                "sections_count": len(s.sections),
                "agents_involved": s.agents_involved,
                "created_at": s.created_at
            }
            for s in franklin_orchestrator.sessions.values()
        ]
    }



# ============================================================================
#                         PERSISTENCE ROUTES
#                    Save/Load Conversations & Sessions
# ============================================================================

# In-memory storage (will be replaced with MongoDB in server.py)
conversations_store: Dict[str, Dict] = {}
tasks_store: Dict[str, Dict] = {}


class SaveConversationRequest(BaseModel):
    user_id: str = "default"
    conversation_type: str  # 'franklin', 'agent', 'bot', 'academy'
    entity_name: str
    messages: List[Dict[str, Any]]


class UpdateConversationRequest(BaseModel):
    messages: List[Dict[str, Any]]


@persistence_router.post("/conversation/save")
async def save_conversation(request: SaveConversationRequest):
    """Save a conversation"""
    import uuid
    conv_id = str(uuid.uuid4())
    conversations_store[conv_id] = {
        "id": conv_id,
        "user_id": request.user_id,
        "type": request.conversation_type,
        "entity_name": request.entity_name,
        "messages": request.messages,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    return {"success": True, "conversation_id": conv_id}


@persistence_router.put("/conversation/{conversation_id}")
async def update_conversation(conversation_id: str, request: UpdateConversationRequest):
    """Update a conversation"""
    if conversation_id not in conversations_store:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversations_store[conversation_id]["messages"] = request.messages
    conversations_store[conversation_id]["updated_at"] = datetime.utcnow().isoformat()
    return {"success": True}


@persistence_router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    if conversation_id not in conversations_store:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversations_store[conversation_id]


@persistence_router.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str, conversation_type: Optional[str] = None):
    """Get all conversations for a user"""
    convs = [c for c in conversations_store.values() if c["user_id"] == user_id]
    if conversation_type:
        convs = [c for c in convs if c["type"] == conversation_type]
    return {"conversations": sorted(convs, key=lambda x: x["updated_at"], reverse=True)}


@persistence_router.get("/conversation/find/{user_id}/{conversation_type}/{entity_name}")
async def find_or_create_conversation(user_id: str, conversation_type: str, entity_name: str):
    """Find existing conversation or create new one"""
    for conv in conversations_store.values():
        if (conv["user_id"] == user_id and 
            conv["type"] == conversation_type and 
            conv["entity_name"] == entity_name):
            return conv
    
    # Create new
    import uuid
    conv_id = str(uuid.uuid4())
    conversations_store[conv_id] = {
        "id": conv_id,
        "user_id": user_id,
        "type": conversation_type,
        "entity_name": entity_name,
        "messages": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    return conversations_store[conv_id]


# ============================================================================
#                         TASK TRACKING ROUTES
#                    Real-time status & proof of work
# ============================================================================

class CreateTaskRequest(BaseModel):
    task_type: str
    description: str
    user_id: str = "default"
    params: Optional[Dict[str, Any]] = None
    steps: Optional[List[str]] = None


class UpdateTaskProgressRequest(BaseModel):
    progress: int
    step_completed: Optional[str] = None
    current_action: Optional[str] = None


@tasks_router.post("/create")
async def create_task(request: CreateTaskRequest):
    """Create a new tracked task"""
    import uuid
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "type": request.task_type,
        "description": request.description,
        "user_id": request.user_id,
        "params": request.params or {},
        "status": "pending",
        "progress": 0,
        "steps": request.steps or [],
        "steps_completed": [],
        "logs": [
            {"event": "created", "message": f"Task created: {request.description}", "timestamp": datetime.utcnow().isoformat()}
        ],
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "last_update": datetime.utcnow().isoformat(),
        "result": None,
        "error": None
    }
    tasks_store[task_id] = task
    return {"success": True, "task_id": task_id, "task": task}


@tasks_router.post("/{task_id}/start")
async def start_task(task_id: str):
    """Start a task"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    task["status"] = "running"
    task["started_at"] = datetime.utcnow().isoformat()
    task["last_update"] = datetime.utcnow().isoformat()
    task["logs"].append({
        "event": "started",
        "message": "Task execution started",
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"success": True, "task": task}


@tasks_router.post("/{task_id}/progress")
async def update_task_progress(task_id: str, request: UpdateTaskProgressRequest):
    """Update task progress - proof of work"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    task["progress"] = request.progress
    task["last_update"] = datetime.utcnow().isoformat()
    
    log_msg = f"Progress: {request.progress}%"
    if request.step_completed:
        task["steps_completed"].append({
            "step": request.step_completed,
            "completed_at": datetime.utcnow().isoformat()
        })
        log_msg += f" - Completed: {request.step_completed}"
    if request.current_action:
        log_msg += f" - Current: {request.current_action}"
    
    task["logs"].append({
        "event": "progress",
        "message": log_msg,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {"success": True, "task": task}


@tasks_router.post("/{task_id}/complete")
async def complete_task(task_id: str, result: Optional[Dict[str, Any]] = None):
    """Mark task as completed"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    task["status"] = "completed"
    task["progress"] = 100
    task["completed_at"] = datetime.utcnow().isoformat()
    task["last_update"] = datetime.utcnow().isoformat()
    task["result"] = result
    task["logs"].append({
        "event": "completed",
        "message": "Task completed successfully",
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"success": True, "task": task}


@tasks_router.post("/{task_id}/fail")
async def fail_task(task_id: str, error: str = "Unknown error"):
    """Mark task as failed"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    task["status"] = "failed"
    task["completed_at"] = datetime.utcnow().isoformat()
    task["last_update"] = datetime.utcnow().isoformat()
    task["error"] = error
    task["logs"].append({
        "event": "failed",
        "message": f"Task failed: {error}",
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"success": True, "task": task}


@tasks_router.get("/{task_id}")
async def get_task(task_id: str):
    """Get task status with proof of work logs"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_store[task_id]


@tasks_router.get("/user/{user_id}")
async def get_user_tasks(user_id: str, status: Optional[str] = None):
    """Get all tasks for a user"""
    tasks = [t for t in tasks_store.values() if t["user_id"] == user_id]
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    return {"tasks": sorted(tasks, key=lambda x: x["created_at"], reverse=True)}


@tasks_router.get("/active")
async def get_active_tasks(user_id: Optional[str] = None):
    """Get all running tasks"""
    tasks = [t for t in tasks_store.values() if t["status"] == "running"]
    if user_id:
        tasks = [t for t in tasks if t["user_id"] == user_id]
    return {"tasks": tasks}
