"""
LITHIUM FILE GENERATOR
Parses LLM output and creates REAL files - not text blobs
"""

import os
import re
import shutil
import zipfile
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Base directory for generated projects
PROJECTS_DIR = Path("/app/generated_projects")

class FileGenerator:
    """
    Parses LLM code output and generates actual files on disk
    """

    def __init__(self):
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    def parse_code_blocks(self, llm_output: str) -> List[Dict]:
        """
        Extract code blocks from LLM output

        Supports formats:
        - ```python filename.py
        - ```python
          # filename.py
        - ### filename.py
          ```python
        - ```language:path/to/file.ext
        """
        files = []

        # Pattern 0: ```language:filepath (most explicit)
        pattern0 = r'```(\w+):([\w/.\_-]+)\s*\n(.*?)```'
        for match in re.finditer(pattern0, llm_output, re.DOTALL):
            lang, filepath, content = match.groups()
            if not any(f["path"] == filepath.strip() for f in files):
                files.append({
                    "path": filepath.strip(),
                    "content": content.strip(),
                    "language": lang.lower()
                })

        # Pattern 1: ```language filepath
        pattern1 = r'```(\w+)\s+([\w/.\_-]+\.[\w]+)\s*\n(.*?)```'
        for match in re.finditer(pattern1, llm_output, re.DOTALL):
            lang, filepath, content = match.groups()
            if not any(f["path"] == filepath.strip() for f in files):
                files.append({
                    "path": filepath.strip(),
                    "content": content.strip(),
                    "language": lang.lower()
                })

        # Pattern 2: ### filepath followed by code block
        pattern2 = r'###\s*([\w/.\_-]+\.[\w]+)\s*\n+```(\w+)\s*\n(.*?)```'
        for match in re.finditer(pattern2, llm_output, re.DOTALL):
            filepath, lang, content = match.groups()
            if not any(f["path"] == filepath.strip() for f in files):
                files.append({
                    "path": filepath.strip(),
                    "content": content.strip(),
                    "language": lang.lower()
                })

        # Pattern 3: # filepath at start of code block
        pattern3 = r'```(\w+)\s*\n#\s*([\w/.\_-]+\.[\w]+)\s*\n(.*?)```'
        for match in re.finditer(pattern3, llm_output, re.DOTALL):
            lang, filepath, content = match.groups()
            if not any(f["path"] == filepath.strip() for f in files):
                files.append({
                    "path": filepath.strip(),
                    "content": content.strip(),
                    "language": lang.lower()
                })

        # If no files found, try generic pattern with filename inference
        if not files:
            pattern4 = r'```(\w+)\s*\n(.*?)```'
            for i, match in enumerate(re.finditer(pattern4, llm_output, re.DOTALL)):
                lang, content = match.groups()
                content = content.strip()

                ext_map = {
                    "python": ".py", "py": ".py",
                    "javascript": ".js", "js": ".js",
                    "typescript": ".ts", "ts": ".ts",
                    "jsx": ".jsx", "tsx": ".tsx",
                    "html": ".html", "css": ".css",
                    "sql": ".sql", "json": ".json",
                    "yaml": ".yaml", "yml": ".yml",
                    "dockerfile": "Dockerfile", "docker": "Dockerfile",
                    "bash": ".sh", "shell": ".sh", "sh": ".sh",
                    "markdown": ".md", "md": ".md"
                }

                ext = ext_map.get(lang.lower(), ".txt")
                
                # Try to extract filename from content
                filename = None
                first_lines = content.split('\n')[:3]
                for line in first_lines:
                    fname_match = re.match(r'^[#/]+\s*([\w_]+\.[\w]+)', line)
                    if fname_match:
                        filename = fname_match.group(1)
                        break

                if not filename:
                    if ext == "Dockerfile":
                        filename = "Dockerfile"
                    else:
                        filename = f"file_{i}{ext}" if i > 0 else f"main{ext}"

                files.append({
                    "path": filename,
                    "content": content,
                    "language": lang.lower()
                })

        return files

    def create_project_structure(self, build_id: str, files: List[Dict]) -> Tuple[Path, Dict]:
        """
        Create actual project directory with all files
        Returns (project_path, stats)
        """
        project_dir = PROJECTS_DIR / build_id
        project_dir.mkdir(parents=True, exist_ok=True)

        stats = {
            "files_created": 0,
            "total_lines": 0,
            "total_bytes": 0,
            "structure": {}
        }

        for f in files:
            filepath = f["path"]
            content = f["content"]
            full_path = project_dir / filepath

            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')

            lines = content.count('\n') + 1
            stats["files_created"] += 1
            stats["total_lines"] += lines
            stats["total_bytes"] += len(content.encode('utf-8'))

            parts = filepath.split('/')
            current = stats["structure"]
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = {"lines": lines, "bytes": len(content)}

        logger.info(f"✓ Created {stats['files_created']} files in {project_dir}")
        return project_dir, stats

    def create_zip(self, build_id: str) -> Optional[Path]:
        """Create a downloadable ZIP of the project"""
        project_dir = PROJECTS_DIR / build_id
        if not project_dir.exists():
            return None

        zip_path = PROJECTS_DIR / f"{build_id}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)

        logger.info(f"✓ Created ZIP: {zip_path}")
        return zip_path

    def get_project_tree(self, build_id: str) -> str:
        """Generate a tree view of the project structure"""
        project_dir = PROJECTS_DIR / build_id
        if not project_dir.exists():
            return "Project not found"

        lines = [f"{build_id}/"]

        def add_tree(path: Path, prefix: str = ""):
            entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{entry.name}")
                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    add_tree(entry, prefix + extension)

        add_tree(project_dir)
        return "\n".join(lines)

    def calculate_checksums(self, build_id: str) -> Dict[str, str]:
        """Calculate SHA-256 checksums for all files"""
        project_dir = PROJECTS_DIR / build_id
        if not project_dir.exists():
            return {}

        checksums = {}
        for filepath in project_dir.rglob("*"):
            if filepath.is_file():
                content = filepath.read_bytes()
                checksum = hashlib.sha256(content).hexdigest()
                rel_path = str(filepath.relative_to(project_dir))
                checksums[rel_path] = checksum

        return checksums

    def verify_files_exist(self, build_id: str, expected_files: List[str]) -> Dict:
        """Verify that expected files exist"""
        project_dir = PROJECTS_DIR / build_id

        result = {
            "all_exist": True,
            "existing": [],
            "missing": []
        }

        for filepath in expected_files:
            full_path = project_dir / filepath
            if full_path.exists():
                result["existing"].append(filepath)
            else:
                result["missing"].append(filepath)
                result["all_exist"] = False

        return result

    def read_file(self, build_id: str, filepath: str) -> Optional[str]:
        """Read a specific file from a project"""
        project_dir = PROJECTS_DIR / build_id
        full_path = project_dir / filepath

        if full_path.exists() and full_path.is_file():
            return full_path.read_text(encoding='utf-8')
        return None

    def delete_project(self, build_id: str) -> bool:
        """Delete a project directory"""
        project_dir = PROJECTS_DIR / build_id
        zip_path = PROJECTS_DIR / f"{build_id}.zip"

        deleted = False
        if project_dir.exists():
            shutil.rmtree(project_dir)
            deleted = True
        if zip_path.exists():
            zip_path.unlink()
            deleted = True

        return deleted


# Global instance
file_generator = FileGenerator()
