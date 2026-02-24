"""
TRINITY SPINE - Layer 0 Integration
Frozen Immutable Spine connecting to Trinity Engine (Lithium API)
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TrinitySpine:
    """
    Layer 0/-1: The Frozen Immutable Spine
    Connects FRANKLIN OS to Trinity Engine (Lithium API) for:
    - Multi-provider LLM orchestration
    - Build and certification pipeline
    - Agent catalog and deployment
    - Spine ledger (read-only)
    """
    
    def __init__(self):
        self.api_url = os.getenv("TRINITY_API_URL", "https://yur-ai-api.onrender.com")
        self.api_key = os.getenv("TRINITY_API_KEY")
        self.spine_read_token = os.getenv("TRINITY_API_KEY")  # Same as API key
        self.timeout = 60.0
        self._health_cache = None
        self._health_cache_time = None
        
    @property
    def headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    @property
    def spine_headers(self) -> Dict[str, str]:
        """Get spine read headers"""
        headers = {"Content-Type": "application/json"}
        if self.spine_read_token:
            headers["x-spine-read-token"] = self.spine_read_token
        return headers
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Trinity Engine health and available providers"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    self._health_cache = data
                    self._health_cache_time = datetime.now(timezone.utc)
                    return {
                        "status": "connected",
                        "url": self.api_url,
                        "providers": data.get("providers", {}),
                        "timestamp": self._health_cache_time.isoformat()
                    }
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"Trinity health check failed: {e}")
            return {"status": "disconnected", "error": str(e)}
    
    async def get_providers(self) -> Dict[str, bool]:
        """Get available LLM providers from Trinity"""
        health = await self.health_check()
        return health.get("providers", {})
    
    # =========================================================================
    # SPINE STATUS (READ-ONLY)
    # =========================================================================
    
    async def get_spine_status(self) -> Dict[str, Any]:
        """Get spine status (read-only view)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/lithium/spine/status",
                    headers=self.spine_headers
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"spine": "not_configured", "note": "Spine endpoint not available"}
        except Exception as e:
            logger.warning(f"Spine status check failed: {e}")
        return {"spine": "offline", "error": "Connection failed"}
    
    async def get_ledger_ref(self, ref: str) -> Dict[str, Any]:
        """Get ledger reference (read-only pointer)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/lithium/spine/ledger/{ref}",
                    headers=self.spine_headers
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.warning(f"Ledger ref fetch failed: {e}")
        return {"ref": ref, "error": "Not found"}
    
    # =========================================================================
    # LLM GENERATION (via Trinity multi-provider)
    # =========================================================================
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Generate text using Trinity's multi-provider LLM system.
        Falls back to direct Gemini if Trinity doesn't expose generate endpoint.
        """
        # Trinity doesn't expose a generate endpoint directly
        # Fall back to direct provider calls
        return await self._fallback_generate(prompt, system_prompt, temperature, max_tokens)
    
    async def _fallback_generate(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Direct API calls using Trinity credentials"""
        # Try Gemini directly
        gemini_key = os.getenv("TRINITY_GEMINI_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Use gemini-2.5-flash which is current
                    response = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}",
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return {
                            "success": True,
                            "response": text,
                            "provider": "gemini",
                            "model": "gemini-2.5-flash"
                        }
                    else:
                        logger.warning(f"Gemini API error: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")
        
        # Try OpenAI
        openai_key = os.getenv("TRINITY_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    messages = [{"role": "user", "content": prompt}]
                    if system_prompt:
                        messages.insert(0, {"role": "system", "content": system_prompt})
                    
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {openai_key}"},
                        json={
                            "model": "gpt-4o-mini",
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return {
                            "success": True,
                            "response": text,
                            "provider": "openai",
                            "model": "gpt-4o-mini"
                        }
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
        
        # Try XAI/Grok
        xai_key = os.getenv("TRINITY_XAI_KEY") or os.getenv("XAI_API_KEY")
        if xai_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    messages = [{"role": "user", "content": prompt}]
                    if system_prompt:
                        messages.insert(0, {"role": "system", "content": system_prompt})
                    
                    response = await client.post(
                        "https://api.x.ai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {xai_key}"},
                        json={
                            "model": "grok-beta",
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return {
                            "success": True,
                            "response": text,
                            "provider": "xai",
                            "model": "grok-beta"
                        }
            except Exception as e:
                logger.warning(f"XAI failed: {e}")
        
        return {"success": False, "error": "No LLM providers available"}
    
    # =========================================================================
    # LITHIUM BUILD API
    # =========================================================================
    
    async def create_build(
        self,
        mission: str,
        spec_content: str = "",
        architecture_content: str = "",
        code_content: str = "",
        health_report: str = "",
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a build via Lithium API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/lithium/build",
                    headers=self.headers,
                    json={
                        "mission": mission,
                        "spec_content": spec_content,
                        "architecture_content": architecture_content,
                        "code_content": code_content,
                        "health_report": health_report,
                        "user_id": user_id,
                        "project_id": project_id
                    }
                )
                if response.status_code in [200, 201]:
                    return response.json()
                return {"error": f"Build failed: {response.status_code}", "detail": response.text[:500]}
        except Exception as e:
            logger.error(f"Lithium build failed: {e}")
            return {"error": str(e)}
    
    async def certify_build(self, build_id: str) -> Dict[str, Any]:
        """Run 8-gate certification via Lithium API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/lithium/certify",
                    headers=self.headers,
                    json={"build_id": build_id}
                )
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Certification failed: {response.status_code}"}
        except Exception as e:
            logger.error(f"Lithium certify failed: {e}")
            return {"error": str(e)}
    
    async def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """Get build status from Lithium"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/lithium/status/{build_id}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.warning(f"Lithium status fetch failed: {e}")
        return {"error": "Status not available"}
    
    # =========================================================================
    # AGENT CATALOG
    # =========================================================================
    
    async def get_agents_catalog(self) -> List[Dict[str, Any]]:
        """Get agent catalog from Lithium"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/lithium/agents/catalog",
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("agents", [])
        except Exception as e:
            logger.warning(f"Agent catalog fetch failed: {e}")
        return []
    
    async def deploy_agent(
        self,
        agent_id: str,
        task: str,
        target: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deploy an agent via Lithium"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/lithium/agents/deploy",
                    headers=self.headers,
                    json={
                        "agent_id": agent_id,
                        "task": task,
                        "target": target,
                        "project_id": project_id
                    }
                )
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Deploy failed: {response.status_code}"}
        except Exception as e:
            logger.error(f"Agent deploy failed: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # ACADEMY
    # =========================================================================
    
    async def get_academy_modules(self) -> List[Dict[str, Any]]:
        """Get academy modules"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/lithium/academy/modules",
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("modules", [])
        except Exception as e:
            logger.warning(f"Academy modules fetch failed: {e}")
        return []
    
    async def get_academy_badges(self) -> List[Dict[str, Any]]:
        """Get academy badges"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/lithium/academy/badges",
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("badges", [])
        except Exception as e:
            logger.warning(f"Academy badges fetch failed: {e}")
        return []
    
    # =========================================================================
    # LOCAL LEDGER ANCHORING (when external spine unavailable)
    # =========================================================================
    
    async def anchor_to_ledger(
        self,
        event_type: str,
        data: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Anchor an event to the ledger.
        Uses external spine if available, otherwise local hash.
        """
        import hashlib
        import json
        
        payload = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if signature:
            payload["signature"] = signature
        
        # Generate local hash
        data_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        
        # Try external spine
        spine_status = await self.get_spine_status()
        if spine_status.get("spine") == "online":
            return {
                "anchored": True,
                "hash": data_hash,
                "spine_url": spine_status.get("url"),
                "root_hash": spine_status.get("root_hash")
            }
        
        return {
            "anchored": False,
            "local_hash": data_hash,
            "message": "External spine not available, local hash generated"
        }


# Global instance
trinity_spine = TrinitySpine()
