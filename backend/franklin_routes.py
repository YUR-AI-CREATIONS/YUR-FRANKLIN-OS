"""
FRANKLIN OS API Routes
Integrates all FRANKLIN OS systems: Runtime, Academy, Bot Tiers, Marketplace, Grok Agent
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

# Create routers
franklin_router = APIRouter(prefix="/api/franklin")
academy_router = APIRouter(prefix="/api/academy")
bots_router = APIRouter(prefix="/api/bots")
marketplace_router = APIRouter(prefix="/api/marketplace")
grok_router = APIRouter(prefix="/api/grok")


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
async def certify_agent(request: CertifyAgentRequest):
    """Certify an agent after program completion"""
    result = agent_academy.certify_agent(
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        program_id=request.program_id,
        ethical_score=request.ethical_score,
        reliability_score=request.reliability_score
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


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
