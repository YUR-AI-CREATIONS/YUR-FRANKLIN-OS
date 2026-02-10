"""
Grok Self-Healing Agent Engine
Architect → Engineer → Healer pattern for autonomous code generation and repair.
"""

import os
import sys
import subprocess
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: str = ""
    error: str = ""
    attempt: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "attempt": self.attempt
        }


@dataclass
class GenesisTask:
    """Task for the Genesis loop"""
    task_id: str
    mission: str
    target_file: str
    status: str = "pending"
    attempts: int = 0
    max_retries: int = 5
    current_code: str = ""
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "mission": self.mission,
            "target_file": self.target_file,
            "status": self.status,
            "attempts": self.attempts,
            "max_retries": self.max_retries,
            "execution_history": self.execution_history,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class GrokAgent:
    """
    Grok Self-Healing Agent - The Trinity Pattern
    - Architect: Designs the solution
    - Engineer: Writes the code
    - Healer: Fixes errors and retries
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-3"
        self.max_retries = 5
        self.tasks: Dict[str, GenesisTask] = {}
        self.output_buffer: List[Dict[str, Any]] = []
        
        if self.api_key:
            logger.info(">>> XAI GROK COGNITIVE CORE ONLINE")
        else:
            logger.warning("XAI_API_KEY not configured - Grok agent will use fallback")
    
    def is_configured(self) -> bool:
        """Check if Grok is properly configured"""
        return bool(self.api_key)
    
    async def chat(self, message: str, history: List[Dict[str, str]] = None) -> Optional[str]:
        """Have a conversation with Grok"""
        if not self.api_key:
            return None
        
        system_prompt = """You are GROK, a powerful AI analysis engine integrated into the FRANKLIN OS platform.
You work alongside Franklin (the primary assistant) to provide deep technical analysis, code review, and intelligent insights.

Your specialties:
- Code analysis and optimization suggestions
- Architecture review and design patterns
- Debugging assistance and error analysis
- Technical explanations and documentation
- Performance optimization recommendations

You are analytical, precise, and technically focused. When asked questions:
- Provide thorough technical analysis
- Suggest improvements and best practices
- Help debug issues with detailed explanations
- Offer code examples when helpful

You are GROK - the analytical brain behind FRANKLIN OS. Be direct, technical, and insightful."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            for msg in history[-10:]:  # Last 10 messages
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        messages.append({"role": "user", "content": message})
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"[GROK CHAT ERROR] {str(e)}")
            return None
    
    async def consult_oracle(self, system_role: str, user_input: str) -> Optional[str]:
        """Interact with Grok API"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_role},
                            {"role": "user", "content": user_input}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 4096
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"[GROK API ERROR] {str(e)}")
            return None
    
    def extract_code(self, response_text: str) -> str:
        """Extract Python code from Markdown blocks"""
        if not response_text:
            return ""
        if "```python" in response_text:
            return response_text.split("```python")[1].split("```")[0].strip()
        elif "```" in response_text:
            return response_text.split("```")[1].split("```")[0].strip()
        return response_text.strip()
    
    def execute_code(self, code: str, filename: str = "temp_script.py") -> ExecutionResult:
        """Execute Python code and capture output"""
        try:
            # Write to temp file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Execute
            result = subprocess.run(
                [sys.executable, filename],
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8"
            )
            
            return ExecutionResult(
                success=(result.returncode == 0),
                output=result.stdout,
                error=result.stderr
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error="Execution timeout (30s)"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    async def architect_phase(self, mission: str) -> str:
        """Phase 1: Architect designs the solution"""
        self._log_output("architect", f"Designing solution for: {mission}")
        
        prompt = f"Write a complete, runnable Python script to: {mission}. Use only standard library if possible. Return ONLY code."
        
        response = await self.consult_oracle(
            "You are a Senior Python Architect specialized in AI systems.",
            prompt
        )
        
        if response:
            code = self.extract_code(response)
            self._log_output("architect", f"Initial design complete ({len(code)} chars)")
            return code
        
        return ""
    
    async def healer_phase(self, code: str, error: str, mission: str) -> str:
        """Phase 3: Healer fixes errors"""
        self._log_output("healer", "Diagnosing and patching...")
        
        fix_prompt = f"""
You are the HEALER. The Python script below failed during execution.

GOAL: {mission}

CURRENT CODE:
{code}

ERROR TRACEBACK:
{error}

INSTRUCTIONS:
1. Analyze the traceback to find the root cause.
2. Fix the logic, syntax, or import errors.
3. Return ONLY the full, corrected Python code inside ```python blocks.
4. Do not offer explanations, just the code.
"""
        
        response = await self.consult_oracle(
            "You are an expert Python Debugger and Systems Architect.",
            fix_prompt
        )
        
        if response:
            new_code = self.extract_code(response)
            self._log_output("healer", f"Patch generated ({len(new_code)} chars)")
            return new_code
        
        return code
    
    async def genesis_loop(self, mission: str, target_file: str = None) -> GenesisTask:
        """
        The Main Self-Healing Loop
        1. Architect designs
        2. Engineer writes
        3. Execute and capture errors
        4. Healer fixes
        5. Repeat until success or max retries
        """
        task_id = f"task_{len(self.tasks) + 1:04d}"
        target = target_file or f"generated_{task_id}.py"
        
        task = GenesisTask(
            task_id=task_id,
            mission=mission,
            target_file=target
        )
        self.tasks[task_id] = task
        task.status = "running"
        
        self._log_output("genesis", f"Starting Genesis Loop: {mission}")
        
        # Phase 1: Architect
        code = await self.architect_phase(mission)
        if not code:
            task.status = "failed"
            self._log_output("genesis", "Architect phase failed - no code generated")
            return task
        
        task.current_code = code
        
        # Write initial code
        with open(target, "w", encoding="utf-8") as f:
            f.write(code)
        self._log_output("engineer", f"Initial code written to {target}")
        
        # Execute and heal loop
        for attempt in range(1, self.max_retries + 1):
            self._log_output("execution", f"Attempt {attempt}/{self.max_retries}")
            
            result = self.execute_code(task.current_code, target)
            result.attempt = attempt
            
            task.attempts = attempt
            task.execution_history.append({
                "attempt": attempt,
                "success": result.success,
                "output": result.output[:500] if result.output else "",
                "error": result.error[:500] if result.error else "",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if result.success:
                self._log_output("success", f"Script executed successfully on attempt {attempt}")
                self._log_output("output", result.output[:500] if result.output else "No output")
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                return task
            
            self._log_output("failure", f"Runtime error: {result.error[:200]}")
            
            # Heal
            if attempt < self.max_retries:
                new_code = await self.healer_phase(task.current_code, result.error, mission)
                if new_code and new_code != task.current_code:
                    task.current_code = new_code
                    with open(target, "w", encoding="utf-8") as f:
                        f.write(new_code)
                    self._log_output("healer", "Patch applied, retrying...")
        
        self._log_output("fatal", "Max retries reached. Manual intervention required.")
        task.status = "failed"
        return task
    
    def _log_output(self, phase: str, message: str):
        """Log output for streaming to frontend"""
        entry = {
            "phase": phase,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.output_buffer.append(entry)
        logger.info(f"[{phase.upper()}] {message}")
    
    def get_output_buffer(self, clear: bool = True) -> List[Dict[str, Any]]:
        """Get and optionally clear the output buffer"""
        buffer = self.output_buffer.copy()
        if clear:
            self.output_buffer = []
        return buffer
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks"""
        return [task.to_dict() for task in self.tasks.values()]
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "configured": self.is_configured(),
            "model": self.model,
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"]),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == "failed"]),
            "running_tasks": len([t for t in self.tasks.values() if t.status == "running"])
        }


# Global Grok agent instance
grok_agent = GrokAgent()
