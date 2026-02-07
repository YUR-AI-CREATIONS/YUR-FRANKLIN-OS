"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         KLING AI VIDEO GENERATOR                              ║
║                                                                              ║
║  Text-to-video and image-to-video generation using Kling AI API.              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import httpx
import jwt
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

KLING_API_BASE = "https://api.klingai.com/v1"


@dataclass
class KlingConfig:
    access_key: str
    secret_key: str
    base_url: str = KLING_API_BASE


class KlingVideoGenerator:
    """
    Kling AI Video Generation Client
    
    Supports:
    - Text-to-video generation
    - Image-to-video generation  
    - Video extension
    - Task status polling
    """
    
    def __init__(self, config: Optional[KlingConfig] = None):
        if config:
            self.access_key = config.access_key
            self.secret_key = config.secret_key
            self.base_url = config.base_url
        else:
            self.access_key = os.getenv("KLING_ACCESS_KEY")
            self.secret_key = os.getenv("KLING_SECRET_KEY")
            self.base_url = KLING_API_BASE
        
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _generate_jwt_token(self) -> str:
        """Generate JWT token for Kling API authentication"""
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 1800,  # 30 min expiry
            "nbf": int(time.time()) - 5
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256", headers=headers)
        return token
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._generate_jwt_token()}"
        }
    
    async def text_to_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model: str = "kling-v1",
        duration: str = "5",  # 5 or 10 seconds
        aspect_ratio: str = "16:9",
        cfg_scale: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt.
        
        Args:
            prompt: Text description of the video
            negative_prompt: What to avoid in the video
            model: kling-v1, kling-v1-5, kling-v1-6
            duration: "5" or "10" seconds
            aspect_ratio: "16:9", "9:16", "1:1"
            cfg_scale: Creativity vs prompt adherence (0-1)
            
        Returns:
            Task info with task_id for polling
        """
        payload = {
            "model_name": model,
            "prompt": prompt,
            "cfg_scale": cfg_scale,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        try:
            response = await self.client.post(
                f"{self.base_url}/videos/text2video",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Kling text-to-video error: {e}")
            return {"error": str(e)}
    
    async def image_to_video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        model: str = "kling-v1",
        duration: str = "5",
        cfg_scale: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate video from an image.
        
        Args:
            image_url: URL of the source image
            prompt: Optional text guidance
            model: kling-v1, kling-v1-5
            duration: "5" or "10" seconds
            cfg_scale: Creativity level
            
        Returns:
            Task info with task_id
        """
        payload = {
            "model_name": model,
            "image": image_url,
            "cfg_scale": cfg_scale,
            "duration": duration
        }
        
        if prompt:
            payload["prompt"] = prompt
        
        try:
            response = await self.client.post(
                f"{self.base_url}/videos/image2video",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Kling image-to-video error: {e}")
            return {"error": str(e)}
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Poll task status and get result when complete.
        
        Args:
            task_id: The task ID from generation request
            
        Returns:
            Task status with video URL when complete
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/videos/text2video/{task_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Kling task status error: {e}")
            return {"error": str(e)}
    
    async def extend_video(
        self,
        video_id: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extend an existing video.
        
        Args:
            video_id: ID of the video to extend
            prompt: Optional guidance for extension
            
        Returns:
            Task info for the extension
        """
        payload = {"video_id": video_id}
        if prompt:
            payload["prompt"] = prompt
        
        try:
            response = await self.client.post(
                f"{self.base_url}/videos/video-extend",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Kling video extend error: {e}")
            return {"error": str(e)}
    
    def is_configured(self) -> bool:
        """Check if Kling API is configured"""
        return bool(self.access_key and self.secret_key)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
kling_generator = KlingVideoGenerator()
