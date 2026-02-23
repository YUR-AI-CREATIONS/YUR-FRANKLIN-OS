"""
TRINITY AI BACKEND - FastAPI Server
Serves the UNIFIED ORCHESTRATOR Cockpit
Port: 8001
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from datetime import datetime
from typing import Optional, List
import logging

from trinity_orchestrator import trinity_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trinity-backend")

# Initialize FastAPI
app = FastAPI(
    title="Trinity AI Orchestration Engine",
    description="Multi-model AI routing and orchestration",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for WebSocket connections and system state
active_connections: List[WebSocket] = []
system_metrics = {
    'status': 'ready',
    'agents_active': 4,
    'tasks_completed': 0,
    'avg_response_time': 0,
    'uptime': '100%',
    'last_task': None
}


@app.get("/health")
async def health_check():
    """System health check"""
    return {
        'status': system_metrics['status'],
        'agents_active': system_metrics['agents_active'],
        'tasks_completed': system_metrics['tasks_completed'],
        'avg_response_time': system_metrics['avg_response_time'],
        'uptime': system_metrics['uptime'],
        'timestamp': datetime.now().isoformat()
    }


@app.post("/execute-task")
async def execute_task(
    task_name: str,
    task_description: str,
    agents: List[str] = None,
    use_grok: bool = False,
    priority: str = "normal"
):
    """
    Execute a task using Trinity orchestration
    """
    try:
        logger.info(f"Executing task: {task_name}")
        
        # Call Trinity engine
        result = await trinity_engine.execute_multi_agent(
            task_name=task_name,
            task_description=task_description,
            agents=agents or [],
            use_grok=use_grok
        )
        
        # Update metrics
        system_metrics['tasks_completed'] += 1
        system_metrics['last_task'] = task_name
        
        # Broadcast to WebSocket clients
        await broadcast_update({
            'type': 'task_completed',
            'task_id': result['execution_id'],
            'task': task_name,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'status': 'success',
            'task_id': result['execution_id'],
            'task': task_name,
            'model_used': result['responses'][0].get('model', 'Unknown') if result['responses'] else 'Unknown',
            'response': result['responses'][0].get('response', '') if result['responses'] else '',
            'agents_used': result['agents_used'],
            'use_grok': use_grok,
            'timestamp': result['timestamp']
        }
    
    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}")
        await broadcast_update({
            'type': 'task_failed',
            'task': task_name,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """Get available Trinity models"""
    return {
        'models': [
            {
                'id': model_id,
                'name': model_info['name'],
                'capabilities': model_info['capabilities'],
                'speciality': model_info['speciality']
            }
            for model_id, model_info in trinity_engine.models.items()
        ]
    }


@app.get("/agents")
async def list_agents():
    """Get available agents"""
    return {
        'agents': [
            {'id': 'sovereign', 'name': 'SOVEREIGN AI', 'role': 'Orchestrator', 'status': 'online'},
            {'id': 'grok', 'name': 'Grok XAI', 'role': 'Intelligence', 'status': 'online'},
            {'id': 'quantum', 'name': 'Quantum Processor', 'role': 'Computation', 'status': 'online'},
            {'id': 'olk7', 'name': 'OLK-7 Kernel', 'role': 'Security', 'status': 'online'},
        ]
    }


@app.get("/tasks")
async def get_tasks(limit: int = 10):
    """Get recent task execution history"""
    recent = trinity_engine.execution_history[-limit:]
    return {
        'tasks': recent,
        'total': len(trinity_engine.execution_history)
    }


@app.websocket("/ws/task-updates/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time task updates"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"Client {client_id} connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process commands
            await websocket.send_json({
                'type': 'ping',
                'message': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
    
    finally:
        active_connections.remove(websocket)
        logger.info(f"Client {client_id} disconnected")


async def broadcast_update(message: dict):
    """Broadcast update to all connected WebSocket clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Failed to broadcast: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 Trinity AI Backend initialized")
    logger.info(f"Available models: {list(trinity_engine.models.keys())}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Trinity AI Backend")
    for connection in active_connections:
        await connection.close()


# Root endpoint
@app.get("/")
def read_root():
    return {
        'service': 'Trinity AI Orchestration Engine',
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'health': '/health',
            'execute': '/execute-task',
            'models': '/models',
            'agents': '/agents',
            'tasks': '/tasks',
            'websocket': '/ws/task-updates/{client_id}'
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
