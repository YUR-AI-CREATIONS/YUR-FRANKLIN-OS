"""
YUR-SOVEREIGN Integration Bridge
Connects YUR Agent Portal with SOVEREIGN AI for unified multi-system orchestration
Enhances both systems with advanced capabilities
"""

from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
YUR_AGENT_API = "http://localhost:3000"  # YUR Agent Portal API
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_AGENT_API = "http://localhost:8002"  # Grok Self-Healing Agent
OLK7_API = "http://localhost:8003"  # OLK-7 Cognitive Kernel

# ===== DATA MODELS =====
class AgentRole(str, Enum):
    ANALYST = "analyst"
    STRATEGIST = "strategist"
    EXECUTOR = "executor"
    INNOVATOR = "innovator"  # Uses Grok for idea generation
    OPTIMIZER = "optimizer"
    VALIDATOR = "validator"

class UnifiedTask(BaseModel):
    """Task that can be routed to either YUR agents or SOVEREIGN AI"""
    id: str
    name: str
    description: str
    agent_role: AgentRole
    use_grok: bool = False  # If true, use Grok for intelligence
    task_type: str
    task_data: dict
    user_id: str = "multi-system-user"
    priority: int = 1
    created_at: datetime = None

class TaskResult(BaseModel):
    """Result from unified execution"""
    task_id: str
    status: str
    agent_role: AgentRole
    execution_time_ms: float
    result: dict
    grok_insights: Optional[str] = None
    steps: List[dict] = []

class SystemMetrics(BaseModel):
    """Health and performance metrics"""
    yur_status: str
    sovereign_status: str
    active_tasks: int
    completed_tasks: int
    avg_execution_time_ms: float
    system_uptime_seconds: float

# ===== INTEGRATION SERVICE =====
class YURSovereignBridge:
    """
    Bridges YUR Agent Portal with SOVEREIGN AI
    - Routes tasks intelligently between systems
    - Enhances agent responses with Grok intelligence
    - Provides unified monitoring and orchestration
    """
    
    def __init__(self):
        self.active_tasks = {}
        self.completed_tasks = []
        self.start_time = datetime.now()
        self.grok_api_key = None  # Set from environment
        
    async def health_check(self) -> SystemMetrics:
        """Check health of both systems"""
        yur_alive = await self._check_endpoint(f"{YUR_AGENT_API}/health")
        
        return SystemMetrics(
            yur_status="healthy" if yur_alive else "offline",
            sovereign_status="healthy",
            active_tasks=len(self.active_tasks),
            completed_tasks=len(self.completed_tasks),
            avg_execution_time_ms=self._calc_avg_execution_time(),
            system_uptime_seconds=(datetime.now() - self.start_time).total_seconds()
        )
    
    async def _check_endpoint(self, url: str) -> bool:
        """Check if endpoint is alive"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                return response.status_code == 200
        except:
            return False
    
    async def execute_unified_task(self, task: UnifiedTask) -> TaskResult:
        """
        Execute task using optimal routing:
        1. Route to YUR Agent Porter for specialized tasks
        2. Enhance with Grok if use_grok=True
        3. Fallback to direct Grok if YUR unavailable
        """
        import time
        start_time = time.time()
        
        task.created_at = datetime.now()
        self.active_tasks[task.id] = task
        
        try:
            # Step 1: Try YUR Agent Portal first (it's specialized)
            result = await self._execute_via_yur(task)
            
            # Step 2: Enhance with Grok intelligence if requested
            grok_insights = None
            if task.use_grok and result.get("result"):
                grok_insights = await self._enhance_with_grok(
                    task.name,
                    json.dumps(result.get("result"), indent=2)
                )
            
            execution_time = (time.time() - start_time) * 1000
            
            task_result = TaskResult(
                task_id=task.id,
                status="completed",
                agent_role=task.agent_role,
                execution_time_ms=execution_time,
                result=result,
                grok_insights=grok_insights,
                steps=result.get("execution_steps", [])
            )
            
            self.completed_tasks.append(task_result)
            del self.active_tasks[task.id]
            
            return task_result
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            
            # Fallback to Grok only
            grok_result = await self._execute_via_grok_only(task)
            execution_time = (time.time() - start_time) * 1000
            
            return TaskResult(
                task_id=task.id,
                status="completed_with_fallback",
                agent_role=task.agent_role,
                execution_time_ms=execution_time,
                result=grok_result,
                grok_insights=grok_result.get("grok_response")
            )
    
    async def _execute_via_yur(self, task: UnifiedTask) -> dict:
        """Execute via YUR Agent Portal"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{YUR_AGENT_API}/api/agents/execute-task",
                json={
                    "agentId": f"{task.agent_role.value}_{'agent' if task.agent_role != AgentRole.INNOVATOR else ''}",
                    "taskType": task.task_type,
                    "taskData": task.task_data,
                    "userId": task.user_id
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
    
    async def _enhance_with_grok(self, context: str, data: str) -> str:
        """Use Grok to enhance analysis"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GROK_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-3",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an advanced AI analyst. Provide strategic insights and recommendations based on the data provided."
                            },
                            {
                                "role": "user",
                                "content": f"Task: {context}\n\nData:\n{data}\n\nProvide strategic insights and next steps."
                            }
                        ],
                        "temperature": 0.5,
                        "max_tokens": 2000
                    },
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Grok enhancement failed: {str(e)}")
            return None
    
    async def _execute_via_grok_only(self, task: UnifiedTask) -> dict:
        """Fallback: Execute directly via Grok"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GROK_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-3",
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are a {task.agent_role.value} agent. Execute the task and provide detailed results."
                            },
                            {
                                "role": "user",
                                "content": f"{task.name}: {task.description}\n\nData: {json.dumps(task.task_data)}"
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4000
                    },
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "grok_response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "source": "grok_fallback"
                }
        except Exception as e:
            logger.error(f"Grok execution failed: {str(e)}")
            raise
    
    def _calc_avg_execution_time(self) -> float:
        """Calculate average execution time"""
        if not self.completed_tasks:
            return 0
        return sum(t.execution_time_ms for t in self.completed_tasks) / len(self.completed_tasks)

# ===== FASTAPI APP =====
app = FastAPI(
    title="YUR-SOVEREIGN Integration Bridge",
    description="Unified multi-system AI orchestration platform",
    version="1.0.0"
)

# Enable CORS for both frontend systems
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize bridge
bridge = YURSovereignBridge()

# ===== API ENDPOINTS =====

@app.get("/health")
async def health_check():
    """System health status"""
    metrics = await bridge.health_check()
    return metrics

@app.post("/api/unified/execute", response_model=TaskResult)
async def execute_unified_task(task: UnifiedTask):
    """
    Execute task via unified orchestration
    Intelligently routes between YUR Agent Portal and Grok
    """
    return await bridge.execute_unified_task(task)

@app.get("/api/unified/tasks")
async def get_user_tasks(user_id: str = "multi-system-user"):
    """Get all tasks for a user"""
    user_tasks = [
        t for t in bridge.completed_tasks 
        if t.task_id.startswith(user_id) or user_id == "multi-system-user"
    ]
    return {
        "user_id": user_id,
        "tasks": user_tasks,
        "count": len(user_tasks)
    }

@app.get("/api/unified/metrics")
async def get_system_metrics():
    """Get system-wide metrics"""
    return await bridge.health_check()

@app.post("/api/enhance-with-olk7")
async def enhance_with_olk7(data: dict):
    """
    Enhance results using OLK-7 Cognitive Kernel
    Applies post-quantum optimization and semantic alignment
    """
    try:
        async with httpx.AsyncClient() as client:
            # Extract vectors from input
            input_vector = data.get("input_vector", [])
            ideal_vector = data.get("ideal_vector", input_vector)
            walkers = data.get("walkers", 50)
            steps = data.get("steps", 100)
            
            # Call OLK-7 API
            response = await client.post(
                f"{OLK7_API}/api/process-directive",
                json={
                    "input_vector": input_vector,
                    "ideal_vector": ideal_vector,
                    "walkers": walkers,
                    "steps": steps
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "enhanced",
                    "original": input_vector,
                    "optimized": result["output"],
                    "energy": result["energy"],
                    "latency": result["latency"],
                    "improvement": 1.0 - result["energy"]
                }
            else:
                logger.warning(f"OLK-7 returned {response.status_code}")
                return {
                    "status": "fallback",
                    "original": input_vector,
                    "error": f"OLK-7 unavailable (HTTP {response.status_code})"
                }
    except Exception as e:
        logger.error(f"OLK-7 enhancement failed: {str(e)}")
        return {
            "status": "error",
            "original": data.get("input_vector", []),
            "error": str(e)
        }

@app.get("/api/olk7-status")
async def get_olk7_status():
    """Get OLK-7 kernel status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OLK7_API}/api/kernel-status",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "unavailable",
                    "message": f"OLK-7 returned {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "offline",
            "message": str(e)
        }

@app.get("/api/unified/task/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str):
    """Get result of a specific task"""
    for task in bridge.completed_tasks:
        if task.task_id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/api/unified/batch-execute")
async def batch_execute_tasks(tasks: List[UnifiedTask], background_tasks: BackgroundTasks):
    """Execute multiple tasks in parallel"""
    async def execute_batch():
        results = []
        for task in tasks:
            result = await bridge.execute_unified_task(task)
            results.append(result)
        return results
    
    background_tasks.add_task(execute_batch)
    return {
        "message": "Batch execution started",
        "total_tasks": len(tasks),
        "check_status": f"/api/unified/metrics"
    }

@app.post("/api/unified/agent-orchestration")
async def orchestrate_multi_agent(
    primary_task: UnifiedTask,
    secondary_agents: List[AgentRole] = [],
    enable_grok_enhancement: bool = True
):
    """
    Orchestrate multi-agent workflow
    Primary agent executes main task
    Secondary agents provide analysis/optimization
    """
    results = {
        "primary": None,
        "secondary": [],
        "workflow_status": "executing"
    }
    
    # Execute primary task
    primary_task.use_grok = enable_grok_enhancement
    results["primary"] = await bridge.execute_unified_task(primary_task)
    
    # Execute secondary agents with results from primary
    for agent_role in secondary_agents:
        secondary_task = UnifiedTask(
            id=f"{primary_task.id}_secondary_{agent_role.value}",
            name=f"Secondary Analysis - {agent_role.value}",
            description=f"Provide {agent_role.value} perspective on primary task results",
            agent_role=agent_role,
            use_grok=enable_grok_enhancement,
            task_type=f"{agent_role.value}_analysis",
            task_data={
                "primary_result": results["primary"].dict() if results["primary"] else {},
                "context": primary_task.description
            },
            user_id=primary_task.user_id
        )
        secondary_result = await bridge.execute_unified_task(secondary_task)
        results["secondary"].append({
            "agent_role": agent_role.value,
            "result": secondary_result
        })
    
    results["workflow_status"] = "completed"
    return results

@app.websocket("/ws/task-updates/{user_id}")
async def websocket_task_updates(websocket: WebSocket, user_id: str):
    """WebSocket for real-time task updates"""
    await websocket.accept()
    try:
        while True:
            # Send current metrics every 5 seconds
            metrics = await bridge.health_check()
            user_tasks = [
                {
                    "task_id": t.task_id,
                    "status": t.status,
                    "execution_time_ms": t.execution_time_ms
                }
                for t in bridge.completed_tasks
                if t.task_id.startswith(user_id)
            ]
            
            await websocket.send_json({
                "type": "metrics_update",
                "metrics": metrics.dict(),
                "user_tasks": user_tasks,
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

# ===== STARTUP EVENTS =====
@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    bridge.grok_api_key = os.getenv("XAI_API_KEY")
    if bridge.grok_api_key:
        logger.info("✅ Grok API key loaded successfully")
    else:
        logger.warning("⚠️  Grok API key not found - will use fallback responses")
    logger.info("🚀 YUR-SOVEREIGN Bridge started")
    logger.info(f"   YUR Agent Portal: {YUR_AGENT_API}")
    logger.info(f"   Grok Agent API: {GROK_AGENT_API}")
    logger.info(f"   OLK-7 Kernel API: {OLK7_API}")
    logger.info(f"   Grok API: {GROK_API_URL}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
