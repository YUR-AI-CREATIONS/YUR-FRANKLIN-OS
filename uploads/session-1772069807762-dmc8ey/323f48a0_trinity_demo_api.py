"""
TRINITY DEMO MODE - Local Mock API
Allows testing the cockpit without external API keys
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime
import random
from typing import Optional, List

app = FastAPI(title="Trinity Demo API", version="1.0.0")

class ExecuteTaskRequest(BaseModel):
    task_name: str
    task_description: str
    agents: Optional[List[str]] = None
    use_grok: bool = False
    priority: str = "normal"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

demo_responses = [
    {
        "analysis": "Market shows strong demand for AI solutions with 45% YoY growth",
        "action_items": ["Increase investment in R&D", "Expand team capabilities"],
        "recommendations": ["Focus on enterprise solutions", "Build partnerships"],
        "next_steps": ["Launch beta program", "Gather customer feedback"]
    },
    {
        "analysis": "Competitive landscape shifting rapidly with 12 new entrants",
        "action_items": ["Monitor competitor moves", "Differentiate offering"],
        "recommendations": ["Invest in unique features", "Build community"],
        "next_steps": ["Quarterly competitive analysis", "Strategy review"]
    },
    {
        "analysis": "Customer satisfaction at 92% with strong retention metrics",
        "action_items": ["Document success patterns", "Train team on best practices"],
        "recommendations": ["Scale operations", "Expand to new verticals"],
        "next_steps": ["Customer advisory board", "Case study development"]
    }
]

task_memory = []

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "yur_status": "healthy",
        "sovereign_status": "healthy",
        "active_tasks": len(task_memory),
        "completed_tasks": len(task_memory),
        "avg_execution_time_ms": 450.0
    }

@app.post("/execute-task")
async def execute_task(request: ExecuteTaskRequest):
    """Execute a task - demo version returns randomized responses"""
    
    task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
    response_data = random.choice(demo_responses)
    
    task_record = {
        "task_id": task_id,
        "task_name": request.task_name,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    task_memory.append(task_record)
    
    return {
        "status": "success",
        "task_id": task_id,
        "task": request.task_name,
        "model_used": "Gemini 2.0 Flash" if request.use_grok else "GPT-4O Mini",
        "response": f"""
Analysis:
{response_data['analysis']}

Action Items:
• {response_data['action_items'][0]}
• {response_data['action_items'][1]}

Recommendations:
• {response_data['recommendations'][0]}
• {response_data['recommendations'][1]}

Next Steps:
• {response_data['next_steps'][0]}
• {response_data['next_steps'][1]}
""",
        "agents_used": request.agents or ['sovereign'],
        "use_grok": request.use_grok,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models")
def list_models():
    return {
        "models": [
            {"id": "gemini", "name": "Gemini 2.0 Flash", "capabilities": ["text", "image", "multimodal"]},
            {"id": "gpt4", "name": "GPT-4O Mini", "capabilities": ["text", "vision"]},
            {"id": "claude", "name": "Claude 3.5 Sonnet", "capabilities": ["text", "analysis"]},
        ]
    }

@app.get("/agents")
def list_agents():
    return {
        "agents": [
            {"id": "sovereign", "name": "SOVEREIGN AI", "role": "Orchestrator", "status": "online"},
            {"id": "grok", "name": "Grok XAI", "role": "Intelligence", "status": "online"},
            {"id": "quantum", "name": "Quantum Processor", "role": "Computation", "status": "online"},
            {"id": "olk7", "name": "OLK-7 Kernel", "role": "Security", "status": "online"},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🎭 TRINITY DEMO MODE - Starting mock API on port 8001")
    print("   This is a demo version - responses are simulated")
    uvicorn.run(app, host="0.0.0.0", port=8001)
