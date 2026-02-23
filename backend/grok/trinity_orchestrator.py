"""
TRINITY AI MASTER ORCHESTRATOR ENGINE
Routes tasks to Gemini, OpenAI, or Anthropic based on task requirements
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
import httpx

class TrinityOrchestrator:
    """Intelligent multi-model orchestration engine"""
    
    def __init__(self):
        self.gemini_key = os.getenv('GOOGLE_API_KEY', '')
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        self.models = {
            'gemini': {
                'name': 'Gemini 2.0 Flash',
                'endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
                'capabilities': ['text', 'image', 'video', 'multimodal', 'reasoning'],
                'max_tokens': 8000,
                'speciality': 'multimodal analysis'
            },
            'gpt4': {
                'name': 'GPT-4O Mini',
                'endpoint': 'https://api.openai.com/v1/chat/completions',
                'capabilities': ['text', 'vision', 'reasoning'],
                'max_tokens': 4096,
                'speciality': 'fast, efficient reasoning'
            },
            'claude': {
                'name': 'Claude 3.5 Sonnet',
                'endpoint': 'https://api.anthropic.com/v1/messages',
                'capabilities': ['text', 'analysis', 'coding'],
                'max_tokens': 4096,
                'speciality': 'deep analysis & coding'
            }
        }
        
        self.execution_history = []
    
    async def classify_task(self, task_name: str, task_description: str) -> str:
        """
        Classify which model is best for this task
        Returns: 'gemini' | 'gpt4' | 'claude'
        """
        task_text = f"{task_name}: {task_description}".lower()
        
        # Classification rules
        if any(word in task_text for word in ['image', 'video', 'visual', 'multimodal', 'analyze image', 'screenshot']):
            return 'gemini'  # Gemini excels at multimodal
        
        if any(word in task_text for word in ['code', 'function', 'debug', 'algorithm', 'schema']):
            return 'claude'  # Claude is best for coding
        
        if any(word in task_text for word in ['quick', 'fast', 'simple', 'summary', 'brief']):
            return 'gpt4'  # GPT-4O Mini is fast & efficient
        
        if any(word in task_text for word in ['market', 'analysis', 'research', 'deep', 'comprehensive']):
            return 'claude'  # Claude for deep analysis
        
        # Default to GPT-4 for general tasks
        return 'gpt4'
    
    async def route_to_model(self, 
                            task_name: str,
                            task_description: str,
                            model_choice: Optional[str] = None,
                            use_grok: bool = False) -> Dict[str, Any]:
        """
        Route task to appropriate model
        """
        
        # Determine which model to use
        if model_choice:
            selected_model = model_choice
        else:
            selected_model = await self.classify_task(task_name, task_description)
        
        model_info = self.models.get(selected_model, self.models['gpt4'])
        
        # Build system prompt
        system_prompt = f"""You are a specialized AI assistant for task: {task_name}
        
Task Requirements:
{task_description}

Provide a structured response with:
1. Analysis
2. Action Items
3. Recommendations
4. Next Steps

{"Additional: Enhance insights with Grok-style intelligence and unconventional perspectives." if use_grok else ""}"""
        
        try:
            if selected_model == 'gemini':
                return await self._call_gemini(system_prompt, task_name)
            elif selected_model == 'gpt4':
                return await self._call_openai(system_prompt, task_name)
            elif selected_model == 'claude':
                return await self._call_anthropic(system_prompt, task_name)
        except Exception as e:
            # Fallback to next model
            return await self._failover(str(e), selected_model, system_prompt, task_name)
    
    async def _call_gemini(self, prompt: str, task_name: str) -> Dict[str, Any]:
        """Call Google Gemini API"""
        if not self.gemini_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.models['gemini']['endpoint']}?key={self.gemini_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    
                    return {
                        'status': 'success',
                        'task': task_name,
                        'model': 'Gemini 2.0 Flash',
                        'response': content,
                        'timestamp': datetime.now().isoformat(),
                        'tokens_used': len(content.split() if content else [])
                    }
                else:
                    raise ValueError(f"Gemini API error: {response.status_code}")
        except Exception as e:
            raise e
    
    async def _call_openai(self, prompt: str, task_name: str) -> Dict[str, Any]:
        """Call OpenAI GPT-4O Mini"""
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.models['gpt4']['endpoint'],
                    headers={
                        "Authorization": f"Bearer {self.openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    return {
                        'status': 'success',
                        'task': task_name,
                        'model': 'GPT-4O Mini',
                        'response': content,
                        'timestamp': datetime.now().isoformat(),
                        'tokens_used': data.get('usage', {}).get('total_tokens', 0)
                    }
                else:
                    raise ValueError(f"OpenAI API error: {response.status_code}")
        except Exception as e:
            raise e
    
    async def _call_anthropic(self, prompt: str, task_name: str) -> Dict[str, Any]:
        """Call Anthropic Claude 3.5 Sonnet"""
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.models['claude']['endpoint'],
                    headers={
                        "x-api-key": self.anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('content', [{}])[0].get('text', '')
                    
                    return {
                        'status': 'success',
                        'task': task_name,
                        'model': 'Claude 3.5 Sonnet',
                        'response': content,
                        'timestamp': datetime.now().isoformat(),
                        'tokens_used': data.get('usage', {}).get('input_tokens', 0) + data.get('usage', {}).get('output_tokens', 0)
                    }
                else:
                    raise ValueError(f"Anthropic API error: {response.status_code}")
        except Exception as e:
            raise e
    
    async def _failover(self, error: str, failed_model: str, prompt: str, task_name: str) -> Dict[str, Any]:
        """Failover to next available model"""
        fallback_order = {
            'gemini': 'gpt4',
            'gpt4': 'claude',
            'claude': 'gpt4'
        }
        
        next_model = fallback_order.get(failed_model, 'gpt4')
        
        try:
            if next_model == 'gemini':
                return await self._call_gemini(prompt, task_name)
            elif next_model == 'gpt4':
                return await self._call_openai(prompt, task_name)
            elif next_model == 'claude':
                return await self._call_anthropic(prompt, task_name)
        except Exception as fallback_error:
            return {
                'status': 'error',
                'task': task_name,
                'error': f"Primary failed ({failed_model}): {error}. Fallback failed ({next_model}): {str(fallback_error)}",
                'timestamp': datetime.now().isoformat()
            }
    
    async def execute_multi_agent(self, 
                                 task_name: str,
                                 task_description: str,
                                 agents: list,
                                 use_grok: bool = False) -> Dict[str, Any]:
        """
        Execute task across multiple agents with Trinity routing
        """
        execution_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        
        results = {
            'execution_id': execution_id,
            'task_name': task_name,
            'timestamp': datetime.now().isoformat(),
            'agents_used': agents or ['sovereign'],
            'use_grok': use_grok,
            'responses': []
        }
        
        # If no specific agents selected, use Trinity routing
        if not agents or agents == ['sovereign']:
            primary_result = await self.route_to_model(task_name, task_description, use_grok=use_grok)
            results['responses'].append(primary_result)
        else:
            # Multi-agent execution
            for agent in agents:
                if agent == 'grok':
                    result = await self.route_to_model(task_name, task_description, model_choice='gpt4', use_grok=True)
                elif agent == 'quantum':
                    result = await self.route_to_model(task_name, task_description, model_choice='claude')
                elif agent == 'olk7':
                    result = await self.route_to_model(task_name, task_description, model_choice='gemini')
                else:
                    result = await self.route_to_model(task_name, task_description)
                
                results['responses'].append(result)
        
        self.execution_history.append(results)
        return results


# Singleton instance
trinity_engine = TrinityOrchestrator()
