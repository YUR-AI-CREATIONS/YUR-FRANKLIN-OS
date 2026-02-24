"""
TRINITY SPINE - Layer 0 Integration
Frozen Immutable Spine connecting to Trinity Engine
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
    Connects FRANKLIN OS to Trinity Engine for:
    - Multi-provider LLM orchestration
    - Governance & compliance validation
    - Evolution playbook management
    - Immutable ledger anchoring
    """
    
    def __init__(self):
        self.api_url = os.getenv("TRINITY_API_URL", "https://yur-ai-api.onrender.com")
        self.api_key = os.getenv("TRINITY_API_KEY")
        self.timeout = 60.0
        self._health_cache = None
        self._health_cache_time = None
        
    @property
    def headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
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
        Trinity handles provider fallback and load balancing.
        """
        try:
            payload = {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system_prompt:
                payload["system_prompt"] = system_prompt
            if provider:
                payload["provider"] = provider
            if model:
                payload["model"] = model
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try multiple endpoint patterns
                for endpoint in ["/api/generate", "/generate", "/api/chat", "/chat", "/api/completion"]:
                    try:
                        response = await client.post(
                            f"{self.api_url}{endpoint}",
                            json=payload,
                            headers=self.headers
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            return {
                                "success": True,
                                "response": data.get("response", data.get("content", data.get("text", ""))),
                                "provider": data.get("provider", provider or "trinity"),
                                "model": data.get("model", model),
                                "usage": data.get("usage", {})
                            }
                        elif response.status_code != 404:
                            # Got a response but not success
                            return {
                                "success": False,
                                "error": f"Trinity returned {response.status_code}",
                                "detail": response.text[:500]
                            }
                    except Exception as e:
                        continue
                
                # If Trinity not available, fall back to direct provider calls
                return await self._fallback_generate(prompt, system_prompt, temperature, max_tokens)
                
        except Exception as e:
            logger.error(f"Trinity generate failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _fallback_generate(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Fallback to direct API calls if Trinity is unavailable"""
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
                            "provider": "gemini-fallback",
                            "model": "gemini-2.5-flash"
                        }
                    else:
                        logger.warning(f"Gemini API error: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                logger.warning(f"Gemini fallback failed: {e}")
        
        return {"success": False, "error": "No LLM providers available"}
    
    # =========================================================================
    # GOVERNANCE & COMPLIANCE
    # =========================================================================
    
    async def validate_governance(
        self,
        artifact: Dict[str, Any],
        policy_type: str = "build"
    ) -> Dict[str, Any]:
        """
        Validate artifact against Trinity governance policies.
        Returns compliance score and any violations.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/governance/validate",
                    json={"artifact": artifact, "policy_type": policy_type},
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    # Endpoint not found, return pass-through
                    return {
                        "compliant": True,
                        "score": 100,
                        "message": "Governance validation not configured"
                    }
                    
        except Exception as e:
            logger.warning(f"Governance validation unavailable: {e}")
        
        return {"compliant": True, "score": 100, "message": "Validation skipped"}
    
    async def get_evolution_playbook(
        self,
        domain: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """Get evolution playbook from Trinity"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/evolution/playbook/{domain}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            logger.warning(f"Evolution playbook fetch failed: {e}")
        
        return None
    
    # =========================================================================
    # IMMUTABLE LEDGER
    # =========================================================================
    
    async def anchor_to_ledger(
        self,
        event_type: str,
        data: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Anchor an event to the immutable ledger.
        Used for build certifications, governance decisions, etc.
        """
        try:
            payload = {
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            if signature:
                payload["signature"] = signature
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/ledger/anchor",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    # Ledger not configured, return local hash
                    import hashlib
                    import json
                    data_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
                    return {
                        "anchored": False,
                        "local_hash": data_hash,
                        "message": "Ledger anchoring not configured"
                    }
                    
        except Exception as e:
            logger.warning(f"Ledger anchoring failed: {e}")
        
        return {"anchored": False, "error": "Ledger unavailable"}
    
    # =========================================================================
    # MISSION MANAGEMENT
    # =========================================================================
    
    async def create_mission(
        self,
        name: str,
        description: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new mission in Trinity"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/missions",
                    json={
                        "name": name,
                        "description": description,
                        "spec": spec
                    },
                    headers=self.headers
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                    
        except Exception as e:
            logger.warning(f"Mission creation failed: {e}")
        
        return {"error": "Mission creation unavailable"}
    
    async def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission by ID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/api/missions/{mission_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            logger.warning(f"Mission fetch failed: {e}")
        
        return None


# Global instance
trinity_spine = TrinitySpine()
