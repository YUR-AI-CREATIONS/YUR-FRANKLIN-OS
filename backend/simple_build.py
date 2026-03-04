"""
SIMPLE BUILD ENDPOINT
One prompt in → Real files out. No bullshit.
"""

import os
import re
import uuid
import json
import hashlib
import httpx
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from zipfile import ZipFile

logger = logging.getLogger(__name__)

# Generated projects directory
PROJECTS_DIR = Path("/app/generated_projects")
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


class SimpleBuildService:
    """
    Simple, reliable build service.
    User says what they want → We call LLM → We create real files.
    """
    
    def __init__(self):
        self.xai_key = os.getenv("XAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY") 
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
    
    async def call_llm(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """
        Call any available LLM. Falls through providers until one works.
        """
        system_prompt = """You are a senior software engineer. Generate complete, working code.

CRITICAL RULES:
1. Output ONLY code blocks with file paths
2. Each file must have: ```language:path/to/file.ext
3. Include ALL imports and dependencies
4. Code must be syntactically correct and runnable
5. Include requirements.txt for Python projects
6. Include package.json for Node projects

Example output format:
```python:main.py
print("Hello World")
```

```txt:requirements.txt
# No dependencies needed
```

Generate clean, production-ready code."""

        providers = []
        
        # Anthropic (most reliable for code)
        if self.anthropic_key:
            providers.append(("anthropic", self._call_anthropic))
        
        # XAI/Grok
        if self.xai_key:
            providers.append(("xai", self._call_xai))
            
        # OpenAI
        if self.openai_key:
            providers.append(("openai", self._call_openai))
            
        # Google
        if self.google_key:
            providers.append(("google", self._call_google))
        
        for name, caller in providers:
            try:
                logger.info(f"[BUILD] Trying {name}...")
                result = await caller(system_prompt, prompt, max_tokens)
                if result:
                    logger.info(f"[BUILD] {name} succeeded")
                    return result
            except Exception as e:
                logger.warning(f"[BUILD] {name} failed: {e}")
                continue
        
        logger.error("[BUILD] All LLM providers failed")
        return None
    
    async def _call_anthropic(self, system: str, prompt: str, max_tokens: int) -> Optional[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-opus-4-6",
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
    
    async def _call_xai(self, system: str, prompt: str, max_tokens: int) -> Optional[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.xai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def _call_openai(self, system: str, prompt: str, max_tokens: int) -> Optional[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def _call_google(self, system: str, prompt: str, max_tokens: int) -> Optional[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.google_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens}
                }
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    
    def parse_code_blocks(self, llm_output: str) -> List[Dict]:
        """
        Parse code blocks from LLM output into files.
        Supports formats:
        - ```language:path/file.ext
        - ```language filename="path/file.ext"
        - ```path/file.ext
        """
        files = []
        
        # Pattern 1: ```language:path/to/file.ext
        pattern1 = r'```(\w+):([^\n]+)\n(.*?)```'
        for match in re.finditer(pattern1, llm_output, re.DOTALL):
            lang, path, content = match.groups()
            files.append({
                "path": path.strip(),
                "content": content.strip(),
                "language": lang
            })
        
        # Pattern 2: ```language filename="path/file.ext"  
        pattern2 = r'```(\w+)\s+filename=["\']([^"\']+)["\']\n(.*?)```'
        for match in re.finditer(pattern2, llm_output, re.DOTALL):
            lang, path, content = match.groups()
            if not any(f["path"] == path.strip() for f in files):
                files.append({
                    "path": path.strip(),
                    "content": content.strip(),
                    "language": lang
                })
        
        # Pattern 3: ```path/file.ext (path as language)
        pattern3 = r'```([a-zA-Z0-9_/\-\.]+\.[a-z]+)\n(.*?)```'
        for match in re.finditer(pattern3, llm_output, re.DOTALL):
            path, content = match.groups()
            if '/' in path or '.' in path:
                if not any(f["path"] == path.strip() for f in files):
                    ext = path.split('.')[-1]
                    lang_map = {'py': 'python', 'js': 'javascript', 'ts': 'typescript', 
                               'html': 'html', 'css': 'css', 'json': 'json', 'md': 'markdown',
                               'txt': 'text', 'sh': 'bash', 'yml': 'yaml', 'yaml': 'yaml'}
                    files.append({
                        "path": path.strip(),
                        "content": content.strip(),
                        "language": lang_map.get(ext, ext)
                    })
        
        # If no files parsed, create single output file
        if not files:
            # Try to extract any code block
            simple_pattern = r'```(?:\w+)?\n(.*?)```'
            matches = re.findall(simple_pattern, llm_output, re.DOTALL)
            if matches:
                files.append({
                    "path": "main.py",
                    "content": matches[0].strip(),
                    "language": "python"
                })
            else:
                files.append({
                    "path": "output.txt",
                    "content": llm_output,
                    "language": "text"
                })
        
        return files
    
    def create_project(self, build_id: str, files: List[Dict]) -> Dict:
        """
        Create actual project directory with real files.
        Returns stats about what was created.
        """
        project_dir = PROJECTS_DIR / build_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        stats = {
            "files_created": 0,
            "total_lines": 0,
            "total_bytes": 0
        }
        
        for f in files:
            file_path = project_dir / f["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = f["content"]
            file_path.write_text(content)
            
            stats["files_created"] += 1
            stats["total_lines"] += len(content.split('\n'))
            stats["total_bytes"] += len(content.encode())
        
        return stats
    
    def create_zip(self, build_id: str) -> Optional[Path]:
        """Create downloadable ZIP of the project."""
        project_dir = PROJECTS_DIR / build_id
        if not project_dir.exists():
            return None
        
        zip_path = PROJECTS_DIR / f"{build_id}.zip"
        with ZipFile(zip_path, 'w') as zf:
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_dir)
                    zf.write(file_path, arcname)
        
        return zip_path
    
    def get_tree(self, build_id: str) -> str:
        """Get directory tree as string."""
        project_dir = PROJECTS_DIR / build_id
        if not project_dir.exists():
            return "Project not found"
        
        lines = [f"{build_id}/"]
        for path in sorted(project_dir.rglob('*')):
            if path.is_file():
                rel = path.relative_to(project_dir)
                depth = len(rel.parts) - 1
                indent = "  " * depth
                lines.append(f"{indent}├── {path.name}")
        
        return '\n'.join(lines)
    
    async def build(self, prompt: str) -> Dict[str, Any]:
        """
        Complete build: prompt → LLM → real files → ready for certification.
        """
        build_id = str(uuid.uuid4())
        logger.info(f"[BUILD {build_id}] Starting: {prompt[:50]}...")
        
        # Step 1: Call LLM
        llm_response = await self.call_llm(f"Build this: {prompt}")
        
        if not llm_response:
            return {
                "success": False,
                "error": "All LLM providers failed. Check API keys.",
                "build_id": build_id
            }
        
        # Step 2: Parse into files
        files = self.parse_code_blocks(llm_response)
        logger.info(f"[BUILD {build_id}] Parsed {len(files)} files")
        
        # Step 3: Create actual project
        stats = self.create_project(build_id, files)
        logger.info(f"[BUILD {build_id}] Created {stats['files_created']} files, {stats['total_lines']} lines")
        
        # Step 4: Create ZIP
        zip_path = self.create_zip(build_id)
        
        # Step 5: Get tree
        tree = self.get_tree(build_id)
        
        # Step 6: Calculate checksums
        checksums = {}
        for f in files:
            checksums[f["path"]] = hashlib.sha256(f["content"].encode()).hexdigest()[:16]
        
        return {
            "success": True,
            "build_id": build_id,
            "status": "completed",
            "prompt": prompt,
            "files": [{"path": f["path"], "language": f["language"], "lines": len(f["content"].split('\n'))} for f in files],
            "file_contents": {f["path"]: f["content"] for f in files},
            "stats": stats,
            "tree": tree,
            "checksums": checksums,
            "zip_available": zip_path is not None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_file(self, build_id: str, filepath: str) -> Optional[str]:
        """Get content of a file from a build."""
        file_path = PROJECTS_DIR / build_id / filepath
        if file_path.exists():
            return file_path.read_text()
        return None
    
    def get_zip_path(self, build_id: str) -> Optional[str]:
        """Get path to ZIP file for download."""
        zip_path = PROJECTS_DIR / f"{build_id}.zip"
        if zip_path.exists():
            return str(zip_path)
        # Try to create it
        created = self.create_zip(build_id)
        return str(created) if created else None


# Global instance
simple_build = SimpleBuildService()
