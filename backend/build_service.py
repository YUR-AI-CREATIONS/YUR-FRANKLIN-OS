"""
LITHIUM BUILD SERVICE
The real build pipeline that creates actual files and runs real certification
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4
import logging

from database import db
from file_generator import file_generator
from certification_engine import certification_engine

logger = logging.getLogger(__name__)


class BuildService:
    """
    Complete build service that:
    1. Orchestrates LLM agents
    2. Parses output into real files
    3. Stores in database
    4. Runs certification
    5. Returns working artifacts
    """
    
    def __init__(self):
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections"""
        if not self._initialized:
            await db.initialize()
            self._initialized = True
    
    async def create_build(
        self,
        mission: str,
        spec_content: str,
        architecture_content: str,
        code_content: str,
        health_report: str,
        user_id: str = None,
        project_id: str = None
    ) -> Dict[str, Any]:
        """
        Create a complete build with real files
        
        Args:
            mission: User's build request
            spec_content: Generated specification
            architecture_content: Generated architecture
            code_content: Generated code (from LLM)
            health_report: Health check results
            user_id: Optional user ID
            project_id: Optional project ID
        
        Returns:
            Complete build record with file paths
        """
        await self.initialize()
        
        build_id = str(uuid4())
        logger.info(f"Creating build {build_id} for: {mission[:50]}...")
        
        # Step 1: Parse code from LLM output into files
        files = file_generator.parse_code_blocks(code_content)
        
        if not files:
            # If no code blocks found, create a single file
            files = [{
                "path": "output.txt",
                "content": code_content,
                "language": "text"
            }]
        
        # Step 2: Create actual project directory with files
        project_dir, stats = file_generator.create_project_structure(build_id, files)
        
        # Step 3: Create ZIP for download
        zip_path = file_generator.create_zip(build_id)
        
        # Step 4: Calculate checksums
        checksums = file_generator.calculate_checksums(build_id)
        
        # Step 5: Generate project tree
        tree = file_generator.get_project_tree(build_id)
        
        # Step 6: Save to database (use our build_id)
        # First save to MongoDB builds collection
        await db.mongo.connect()
        now = datetime.now(timezone.utc)
        await db.mongo.db["builds"].insert_one({
            "id": build_id,
            "mission": mission,
            "user_id": user_id,
            "project_id": project_id,
            "status": "completed",
            "spec_content": spec_content,
            "architecture_content": architecture_content,
            "code_content": code_content,
            "health_report": health_report,
            "artifacts_path": str(project_dir),
            "file_count": stats["files_created"],
            "total_lines": stats["total_lines"],
            "created_at": now,
            "completed_at": now
        })
        
        # Step 7: Save artifacts to MongoDB
        files_with_checksums = []
        for f in files:
            f_copy = f.copy()
            f_copy["checksum"] = checksums.get(f["path"], "")
            files_with_checksums.append(f_copy)
        
        await db.save_build_artifacts(build_id, files_with_checksums)
        
        logger.info(f"✓ Build {build_id} created: {stats['files_created']} files, {stats['total_lines']} lines")
        
        return {
            "build_id": build_id,
            "status": "completed",
            "mission": mission,
            "files": [{"path": f["path"], "language": f["language"]} for f in files],
            "stats": stats,
            "checksums": checksums,
            "tree": tree,
            "zip_available": zip_path is not None,
            "artifacts_path": str(project_dir)
        }
    
    async def certify_build(self, build_id: str) -> Dict[str, Any]:
        """
        Run 8-gate certification on a build
        
        Args:
            build_id: The build to certify
        
        Returns:
            Certification results
        """
        await self.initialize()
        
        logger.info(f"Starting certification for build {build_id}")
        
        # Get build record
        build = await db.get_build(build_id)
        if not build:
            raise ValueError(f"Build {build_id} not found")
        
        # Get artifacts
        artifacts = await db.get_build_artifacts(build_id)
        files = artifacts.get("files", []) if artifacts else []
        
        # Run all 8 gates
        cert_results = await certification_engine.run_all_gates(
            build_id=build_id,
            mission=build.get("mission", ""),
            spec=build.get("spec_content", ""),
            architecture=build.get("architecture_content", ""),
            files=files
        )
        
        # Save certification to database
        cert_record = await db.create_certification(build_id)
        
        # Update each gate
        for gate in cert_results["gates"]:
            await db.update_gate(
                cert_record["id"],
                gate["gate_num"],
                gate["passed"],
                {
                    "score": gate["score"],
                    "checks": gate["details"].get("checks", []),
                    "errors": gate["errors"],
                    "warnings": gate["warnings"]
                }
            )
        
        # Finalize certification
        await db.finalize_certification(cert_record["id"])
        
        # Update build status
        if cert_results["all_passed"]:
            await db.update_build(build_id, status="certified")
        
        logger.info(f"✓ Certification complete: {'PASSED' if cert_results['all_passed'] else 'FAILED'}")
        
        return {
            "build_id": build_id,
            "certification_id": cert_record["id"],
            "all_gates_passed": cert_results["all_passed"],
            "total_score": cert_results["total_score"],
            "passed_gates": cert_results["passed_gates"],
            "failed_gates": cert_results["failed_gates"],
            "certification_hash": cert_results.get("certification_hash"),
            "certified_at": cert_results.get("certified_at"),
            "gates": cert_results["gates"]
        }
    
    async def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """Get complete status of a build including certification"""
        await self.initialize()
        
        build = await db.get_build(build_id)
        if not build:
            return {"error": "Build not found"}
        
        certification = await db.get_certification(build_id)
        artifacts = await db.get_build_artifacts(build_id)
        
        return {
            "build": {
                "id": str(build.get("id")),
                "project_id": build.get("project_id"),
                "mission": build.get("mission"),
                "status": build.get("status"),
                "file_count": build.get("file_count"),
                "total_lines": build.get("total_lines"),
                "created_at": build.get("created_at").isoformat() if build.get("created_at") else None,
                "completed_at": build.get("completed_at").isoformat() if build.get("completed_at") else None
            },
            "certification": {
                "exists": certification is not None,
                "all_passed": certification.get("all_gates_passed") if certification else False,
                "hash": certification.get("certification_hash") if certification else None,
                "certified_at": certification.get("certified_at").isoformat() if certification and certification.get("certified_at") else None,
                "gates": [
                    {
                        "gate": i,
                        "passed": certification.get(f"gate_{i}_passed") if certification else False
                    }
                    for i in range(1, 9)
                ] if certification else []
            },
            "artifacts": {
                "file_count": artifacts.get("file_count") if artifacts else 0,
                "files": [f.get("path") for f in artifacts.get("files", [])] if artifacts else []
            }
        }
    
    async def get_file_content(self, build_id: str, filepath: str) -> Optional[str]:
        """Get content of a specific file from a build"""
        return file_generator.read_file(build_id, filepath)
    
    async def get_project_tree(self, build_id: str) -> str:
        """Get project tree structure"""
        return file_generator.get_project_tree(build_id)
    
    async def download_zip_path(self, build_id: str) -> Optional[str]:
        """Get path to downloadable ZIP"""
        from pathlib import Path
        zip_path = Path("/app/generated_projects") / f"{build_id}.zip"
        if zip_path.exists():
            return str(zip_path)
        
        # Create if doesn't exist
        new_zip = file_generator.create_zip(build_id)
        return str(new_zip) if new_zip else None


# Global instance
build_service = BuildService()
