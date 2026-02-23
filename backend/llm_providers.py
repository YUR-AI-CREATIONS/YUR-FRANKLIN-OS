"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         LLM PROVIDER ABSTRACTION                             ║
║                                                                              ║
║  Supports multiple LLM backends:                                             ║
║  - Cloud: Claude, GPT-4, Gemini (via Emergent Key)                          ║
║  - Local: Ollama (Llama 3, Mistral, CodeLlama, etc.)                        ║
║                                                                              ║
║  Switch between modes without code changes.                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class LLMMode(Enum):
    CLOUD = "cloud"      # Claude/GPT via Emergent
    LOCAL = "local"      # Ollama local inference
    HYBRID = "hybrid"    # Local for dev, cloud for complex tasks


@dataclass
class LLMConfig:
    """LLM Provider Configuration"""
    mode: LLMMode
    # Cloud settings
    cloud_provider: str = "anthropic"
    cloud_model: str = "claude-sonnet-4-5-20250929"
    emergent_key: Optional[str] = None
    # Local settings
    local_url: str = "http://localhost:11434"
    local_model: str = "llama3.1:8b"  # Default to Llama 3.1 8B
    # Fallback settings
    fallback_to_cloud: bool = True
    max_retries: int = 3


class BaseLLMProvider(ABC):
    """Abstract base for LLM providers"""
    
    @abstractmethod
    async def generate(self, system_prompt: str, user_message: str, 
                      temperature: float = 0.7) -> str:
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass


class OllamaProvider(BaseLLMProvider):
    """
    Local LLM via Ollama
    
    Supports: Llama 3, Llama 3.1, Mistral, CodeLlama, Phi-3, Gemma, etc.
    
    Setup:
    1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
    2. Pull model: ollama pull llama3.1:8b
    3. Ollama runs automatically on localhost:11434
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate(self, system_prompt: str, user_message: str,
                      temperature: float = 0.7) -> str:
        """Generate response using Ollama"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 4096
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            logging.error(f"Ollama error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    async def list_models(self) -> List[str]:
        """List available local models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except:
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=600.0  # Models can be large
            )
            return response.status_code == 200
        except:
            return False


class CloudProvider(BaseLLMProvider):
    """
    Cloud LLM Provider
    
    Supports:
    - Direct OpenAI API (set LLM_PROVIDER=openai)
    - Direct Anthropic API (set LLM_PROVIDER=anthropic_direct)
    - xAI/Grok API (set LLM_PROVIDER=xai)
    - Google/Gemini API (set LLM_PROVIDER=google)
    - Emergent Universal Key (set LLM_PROVIDER=emergent)
    """
    
    def __init__(self, api_key: str, provider: str = "anthropic",
                 model: str = "claude-sonnet-4-5-20250929",
                 provider_type: str = "emergent"):
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.provider_type = provider_type
        
        if provider_type == "emergent":
            # Removed emergentintegrations dependency - using local implementation
            raise NotImplementedError("Emergent provider not available - use anthropic, openai, xai, or google instead")
            # from emergentintegrations.llm.chat import LlmChat, UserMessage
            # self.LlmChat = LlmChat
            # self.UserMessage = UserMessage
        elif provider_type == "openai":
            import openai
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
        elif provider_type == "xai":
            import openai
            self.openai_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
        elif provider_type == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
        elif provider_type == "anthropic_direct":
            import anthropic
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate(self, system_prompt: str, user_message: str,
                      temperature: float = 0.7) -> str:
        """Generate response using cloud LLM"""
        
        if self.provider_type == "emergent":
            # Removed emergentintegrations dependency
            raise NotImplementedError("Emergent provider not available - use anthropic, openai, xai, or google instead")
            # chat = self.LlmChat(
            #     api_key=self.api_key,
            #     session_id=f"cloud_{id(self)}",
            #     system_message=system_prompt
            # )
            # chat.with_model(self.provider, self.model)
            # message = self.UserMessage(text=user_message)
            # response = await chat.send_message(message)
            # return response
            
        elif self.provider_type in ["openai", "xai"]:
            response = await self.openai_client.chat.completions.create(
                model=self.model or ("grok-beta" if self.provider_type == "xai" else "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        
        elif self.provider_type == "google":
            model = self.genai.GenerativeModel(
                model_name=self.model or "gemini-1.5-pro",
                system_instruction=system_prompt
            )
            response = await model.generate_content_async(
                user_message,
                generation_config={"temperature": temperature}
            )
            return response.text
            
        elif self.provider_type == "anthropic_direct":
            response = await self.anthropic_client.messages.create(
                model=self.model or "claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature
            )
            return response.content[0].text
    
    async def health_check(self) -> bool:
        """Check if cloud API is accessible"""
        try:
            return bool(self.api_key)
        except:
            return False


class HybridLLMProvider:
    """
    Intelligent routing between local and cloud LLMs
    
    Supports multiple API key sources:
    - OPENAI_API_KEY: Direct OpenAI (GPT-4o, GPT-4, etc.)
    - ANTHROPIC_API_KEY: Direct Anthropic (Claude)
    - EMERGENT_LLM_KEY: Emergent Universal Key
    
    Set LLM_PROVIDER env var to: "openai", "anthropic_direct", or "emergent"
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.local_provider: Optional[OllamaProvider] = None
        self.cloud_provider: Optional[CloudProvider] = None
        self.local_available = False
        self.request_count = {"local": 0, "cloud": 0}
        self.active_provider_type = None
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on env vars"""
        # Always try to set up local
        self.local_provider = OllamaProvider(
            base_url=self.config.local_url,
            model=self.config.local_model
        )
        
        # Check for API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        xai_key = os.getenv("XAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        emergent_key = self.config.emergent_key or os.getenv("EMERGENT_LLM_KEY")
        provider_pref = os.getenv("LLM_PROVIDER", "emergent").lower()
        
        # Set up cloud provider based on preference and available keys
        if provider_pref == "openai" and openai_key:
            self.cloud_provider = CloudProvider(
                api_key=openai_key,
                provider="openai",
                model="gpt-4o",
                provider_type="openai"
            )
            self.active_provider_type = "openai"
            logging.info("Using OpenAI API directly")
        
        elif provider_pref == "xai" and xai_key:
            self.cloud_provider = CloudProvider(
                api_key=xai_key,
                provider="xai",
                model="grok-beta",
                provider_type="xai"
            )
            self.active_provider_type = "xai"
            logging.info("Using xAI/Grok API")
        
        elif provider_pref == "google" and google_key:
            self.cloud_provider = CloudProvider(
                api_key=google_key,
                provider="google",
                model="gemini-1.5-pro",
                provider_type="google"
            )
            self.active_provider_type = "google"
            logging.info("Using Google/Gemini API")
            
        elif provider_pref == "anthropic_direct" and anthropic_key:
            self.cloud_provider = CloudProvider(
                api_key=anthropic_key,
                provider="anthropic",
                model="claude-sonnet-4-5-20250929",
                provider_type="anthropic_direct"
            )
            self.active_provider_type = "anthropic_direct"
            logging.info("Using Anthropic API directly")
            
        elif emergent_key and False:  # Disabled emergent provider
            self.cloud_provider = CloudProvider(
                api_key=emergent_key,
                provider=self.config.cloud_provider,
                model=self.config.cloud_model,
                provider_type="emergent"
            )
            self.active_provider_type = "emergent"
            logging.info("Using Emergent Universal Key")
            
        else:
            logging.warning("No cloud LLM API key found")
    
    async def initialize(self):
        """Async initialization - check provider availability"""
        if self.local_provider:
            self.local_available = await self.local_provider.health_check()
            if self.local_available:
                logging.info(f"Local LLM available: {self.config.local_model}")
            else:
                logging.warning("Local LLM (Ollama) not available")
    
    async def generate(self, system_prompt: str, user_message: str,
                      prefer_local: bool = True,
                      temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate response with intelligent routing
        
        Args:
            system_prompt: System instruction
            user_message: User input
            prefer_local: Use local if available (saves cost)
            temperature: Creativity (0.0-1.0)
            
        Returns:
            Dict with response, provider used, and metadata
        """
        provider_used = None
        response = None
        error = None
        
        # Determine which provider to use
        use_local = (
            self.config.mode in [LLMMode.LOCAL, LLMMode.HYBRID] and
            self.local_available and
            prefer_local
        )
        
        use_cloud = (
            self.config.mode in [LLMMode.CLOUD, LLMMode.HYBRID] and
            self.cloud_provider is not None
        )
        
        # Try local first if preferred
        if use_local:
            try:
                response = await self.local_provider.generate(
                    system_prompt, user_message, temperature
                )
                provider_used = "local"
                self.request_count["local"] += 1
            except Exception as e:
                error = str(e)
                logging.warning(f"Local LLM failed: {e}")
                
                # Fallback to cloud if configured
                if self.config.fallback_to_cloud and use_cloud:
                    logging.info("Falling back to cloud LLM")
                    use_local = False
        
        # Use cloud if local not used/failed
        if not use_local and use_cloud and response is None:
            try:
                response = await self._cloud_with_retry(
                    system_prompt, user_message, temperature
                )
                provider_used = "cloud"
                self.request_count["cloud"] += 1
            except Exception as e:
                error = str(e)
                logging.error(f"Cloud LLM failed: {e}")
        
        if response is None:
            raise Exception(f"All LLM providers failed. Last error: {error}")
        
        return {
            "response": response,
            "provider": provider_used,
            "model": self.config.local_model if provider_used == "local" else self.config.cloud_model,
            "request_counts": self.request_count.copy()
        }
    
    async def _cloud_with_retry(self, system_prompt: str, user_message: str,
                                temperature: float) -> str:
        """Cloud call with retry logic"""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await self.cloud_provider.generate(
                    system_prompt, user_message, temperature
                )
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Retry on transient errors
                if any(code in error_str for code in ['502', '503', '504', 'timeout', 'gateway']):
                    wait_time = (2 ** attempt) + 1
                    logging.warning(f"Transient error, retry {attempt + 1}/{self.config.max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise
        
        raise last_error
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status"""
        return {
            "mode": self.config.mode.value,
            "local_available": self.local_available,
            "local_model": self.config.local_model,
            "cloud_available": self.cloud_provider is not None,
            "cloud_model": self.config.cloud_model,
            "cloud_provider_type": self.active_provider_type,
            "request_counts": self.request_count,
            "fallback_enabled": self.config.fallback_to_cloud,
            "api_keys_configured": {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "xai": bool(os.getenv("XAI_API_KEY")),
                "google": bool(os.getenv("GOOGLE_API_KEY")),
                "emergent": bool(os.getenv("EMERGENT_LLM_KEY"))
            }
        }


# ============================================================================
#                         RECOMMENDED LOCAL MODELS
# ============================================================================

RECOMMENDED_MODELS = {
    "general": {
        "llama3.1:8b": {
            "description": "Latest Llama 3.1 - excellent general purpose",
            "size": "4.7GB",
            "speed": "fast",
            "quality": "high"
        },
        "llama3.1:70b": {
            "description": "Llama 3.1 70B - near cloud quality",
            "size": "40GB",
            "speed": "slow",
            "quality": "very high",
            "requires": "32GB+ RAM or GPU"
        },
        "mistral:7b": {
            "description": "Fast and capable general model",
            "size": "4.1GB", 
            "speed": "very fast",
            "quality": "good"
        }
    },
    "coding": {
        "codellama:13b": {
            "description": "Specialized for code generation",
            "size": "7.4GB",
            "speed": "medium",
            "quality": "high for code"
        },
        "deepseek-coder:6.7b": {
            "description": "Strong coding capabilities",
            "size": "3.8GB",
            "speed": "fast",
            "quality": "high for code"
        }
    },
    "reasoning": {
        "phi3:14b": {
            "description": "Microsoft Phi-3 - strong reasoning",
            "size": "7.9GB",
            "speed": "medium",
            "quality": "high"
        },
        "gemma2:9b": {
            "description": "Google Gemma 2 - balanced",
            "size": "5.5GB",
            "speed": "fast",
            "quality": "good"
        }
    }
}


def get_recommended_model(use_case: str = "general", 
                         max_size_gb: float = 8.0) -> str:
    """Get recommended model for use case within size constraints"""
    models = RECOMMENDED_MODELS.get(use_case, RECOMMENDED_MODELS["general"])
    
    for model_name, info in models.items():
        size_str = info["size"].replace("GB", "")
        if float(size_str) <= max_size_gb:
            return model_name
    
    # Default fallback
    return "llama3.1:8b"
