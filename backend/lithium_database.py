"""
LITHIUM DATABASE MANAGER
Supabase Client + MongoDB dual-layer persistence
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# Try to import Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase client not available")


# ============================================================================
# SCHEMA SQL - Run this in Supabase SQL Editor
# ============================================================================

SCHEMA_SQL = """
-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PROJECTS TABLE
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tech_stack VARCHAR(100),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- BUILDS TABLE (standalone, no FK for now)
CREATE TABLE IF NOT EXISTS builds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    build_id VARCHAR(100) UNIQUE NOT NULL,
    mission TEXT NOT NULL,
    tech_stack VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    files_count INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    total_bytes INTEGER DEFAULT 0,
    tree TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- CERTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    build_id VARCHAR(100) NOT NULL,
    certification_hash VARCHAR(64),
    total_score FLOAT DEFAULT 0,
    passed_gates INTEGER DEFAULT 0,
    failed_gates INTEGER DEFAULT 0,
    all_passed BOOLEAN DEFAULT FALSE,
    gate_results JSONB,
    certified_at TIMESTAMPTZ,
    signed_by VARCHAR(100) DEFAULT 'FRANKLIN'
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_builds_build_id ON builds(build_id);
CREATE INDEX IF NOT EXISTS idx_certifications_build_id ON certifications(build_id);
"""


class LithiumDatabase:
    """
    Dual-layer database manager:
    - Supabase (PostgreSQL) for structured data via client library
    - MongoDB for documents and file contents
    """

    def __init__(self):
        # Supabase
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase: Optional[Client] = None
        
        # MongoDB
        self.mongo_url = os.getenv("MONGO_URL")
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.mongo_db = None
        
        self._initialized = False
        self._tables_exist = False

    async def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
        
        # Connect to Supabase
        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                logger.info("✓ Supabase client initialized")
                
                # Check if tables exist by trying a simple query
                await self._check_tables()
            except Exception as e:
                logger.error(f"✗ Supabase initialization failed: {e}")
                self.supabase = None
        else:
            logger.warning("Supabase not configured (missing URL or key)")
        
        # Connect to MongoDB
        if self.mongo_url:
            try:
                self.mongo_client = AsyncIOMotorClient(self.mongo_url)
                self.mongo_db = self.mongo_client[os.getenv("DB_NAME", "franklin_os")]
                await self.mongo_db.command("ping")
                logger.info("✓ MongoDB connected")
            except Exception as e:
                logger.error(f"✗ MongoDB connection failed: {e}")
                self.mongo_db = None
        
        self._initialized = True

    async def _check_tables(self):
        """Check if required tables exist in Supabase"""
        if not self.supabase:
            return
        
        try:
            # Try to query the builds table
            result = self.supabase.table("builds").select("build_id").limit(1).execute()
            self._tables_exist = True
            logger.info("✓ Supabase tables verified")
        except Exception as e:
            error_str = str(e).lower()
            if "does not exist" in error_str or "relation" in error_str:
                logger.warning("⚠ Supabase tables don't exist yet. Run SCHEMA_SQL in SQL Editor.")
                self._tables_exist = False
            else:
                logger.warning(f"⚠ Supabase table check: {e}")
                self._tables_exist = False

    # =========================================================================
    # BUILD OPERATIONS
    # =========================================================================

    async def save_build(self, build_data: Dict) -> Optional[Dict]:
        """Save a build to both Supabase and MongoDB"""
        saved_supabase = False
        saved_mongo = False
        
        build_id = build_data["build_id"]
        
        # Prepare data for Supabase (structured)
        supabase_data = {
            "build_id": build_id,
            "mission": build_data.get("prompt", build_data.get("mission", "")),
            "tech_stack": build_data.get("tech_stack"),
            "status": build_data.get("status", "completed"),
            "files_count": build_data.get("stats", {}).get("files_created", 0),
            "total_lines": build_data.get("stats", {}).get("total_lines", 0),
            "total_bytes": build_data.get("stats", {}).get("total_bytes", 0),
            "tree": build_data.get("tree"),
        }
        
        if build_data.get("status") == "completed":
            supabase_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save to Supabase
        if self.supabase and self._tables_exist:
            try:
                # Upsert - insert or update
                result = self.supabase.table("builds").upsert(
                    supabase_data,
                    on_conflict="build_id"
                ).execute()
                saved_supabase = True
                logger.info(f"Build {build_id} saved to Supabase")
            except Exception as e:
                logger.error(f"Supabase save failed: {e}")
        
        # Save to MongoDB (with file contents)
        if self.mongo_db is not None:
            try:
                mongo_doc = {
                    "build_id": build_id,
                    "mission": build_data.get("prompt", build_data.get("mission", "")),
                    "tech_stack": build_data.get("tech_stack"),
                    "status": build_data.get("status", "completed"),
                    "files_count": build_data.get("stats", {}).get("files_created", 0),
                    "total_lines": build_data.get("stats", {}).get("total_lines", 0),
                    "total_bytes": build_data.get("stats", {}).get("total_bytes", 0),
                    "tree": build_data.get("tree"),
                    "file_contents": build_data.get("file_contents", {}),
                    "created_at": datetime.now(timezone.utc),
                    "completed_at": datetime.now(timezone.utc) if build_data.get("status") == "completed" else None
                }
                
                await self.mongo_db.builds.update_one(
                    {"build_id": build_id},
                    {"$set": mongo_doc},
                    upsert=True
                )
                saved_mongo = True
                logger.info(f"Build {build_id} saved to MongoDB")
            except Exception as e:
                logger.error(f"MongoDB save failed: {e}")
        
        return build_data if (saved_supabase or saved_mongo) else None

    async def get_build(self, build_id: str) -> Optional[Dict]:
        """Get a build by ID"""
        build = None
        
        # Try Supabase first for metadata
        if self.supabase and self._tables_exist:
            try:
                result = self.supabase.table("builds").select("*").eq("build_id", build_id).single().execute()
                if result.data:
                    build = result.data
            except Exception as e:
                logger.debug(f"Supabase get_build: {e}")
        
        # Get file contents from MongoDB
        if self.mongo_db is not None:
            try:
                mongo_doc = await self.mongo_db.builds.find_one({"build_id": build_id})
                if mongo_doc:
                    mongo_doc.pop("_id", None)
                    if build:
                        build["file_contents"] = mongo_doc.get("file_contents", {})
                    else:
                        build = mongo_doc
            except Exception as e:
                logger.error(f"MongoDB get_build failed: {e}")
        
        return build

    async def get_recent_builds(self, limit: int = 20) -> List[Dict]:
        """Get recent builds"""
        builds = []
        
        # Try Supabase first
        if self.supabase and self._tables_exist:
            try:
                result = self.supabase.table("builds").select(
                    "build_id, mission, tech_stack, status, files_count, total_lines, created_at"
                ).order("created_at", desc=True).limit(limit).execute()
                
                if result.data:
                    builds = result.data
            except Exception as e:
                logger.debug(f"Supabase get_recent_builds: {e}")
        
        # Fallback to MongoDB
        if not builds and self.mongo_db is not None:
            try:
                cursor = self.mongo_db.builds.find(
                    {}, 
                    {"_id": 0, "file_contents": 0}
                ).sort("created_at", -1).limit(limit)
                
                async for doc in cursor:
                    builds.append(doc)
            except Exception as e:
                logger.error(f"MongoDB get_recent_builds failed: {e}")
        
        return builds

    # =========================================================================
    # CERTIFICATION OPERATIONS
    # =========================================================================

    async def save_certification(self, cert_data: Dict) -> Optional[Dict]:
        """Save certification results"""
        build_id = cert_data["build_id"]
        
        # Prepare data for Supabase
        import json
        supabase_data = {
            "build_id": build_id,
            "certification_hash": cert_data.get("certification_hash"),
            "total_score": cert_data.get("total_score", 0),
            "passed_gates": cert_data.get("passed_gates", 0),
            "failed_gates": cert_data.get("failed_gates", 0),
            "all_passed": cert_data.get("all_passed", False),
            "gate_results": json.dumps(cert_data.get("gates", [])),
            "signed_by": cert_data.get("signed_by", "FRANKLIN")
        }
        
        if cert_data.get("all_passed"):
            supabase_data["certified_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save to Supabase
        if self.supabase and self._tables_exist:
            try:
                result = self.supabase.table("certifications").insert(supabase_data).execute()
                logger.info(f"Certification for {build_id} saved to Supabase")
                return cert_data
            except Exception as e:
                logger.error(f"Supabase save_certification failed: {e}")
        
        # Fallback to MongoDB
        if self.mongo_db is not None:
            try:
                cert_data["created_at"] = datetime.now(timezone.utc)
                await self.mongo_db.certifications.update_one(
                    {"build_id": build_id},
                    {"$set": cert_data},
                    upsert=True
                )
                logger.info(f"Certification for {build_id} saved to MongoDB")
                return cert_data
            except Exception as e:
                logger.error(f"MongoDB save_certification failed: {e}")
        
        return None

    async def get_certification(self, build_id: str) -> Optional[Dict]:
        """Get certification for a build"""
        # Try Supabase first
        if self.supabase and self._tables_exist:
            try:
                result = self.supabase.table("certifications").select("*").eq(
                    "build_id", build_id
                ).order("certified_at", desc=True).limit(1).execute()
                
                if result.data:
                    return result.data[0]
            except Exception as e:
                logger.debug(f"Supabase get_certification: {e}")
        
        # Fallback to MongoDB
        if self.mongo_db is not None:
            try:
                doc = await self.mongo_db.certifications.find_one({"build_id": build_id})
                if doc:
                    doc.pop("_id", None)
                    return doc
            except Exception as e:
                logger.error(f"MongoDB get_certification failed: {e}")
        
        return None

    # =========================================================================
    # HEALTH CHECK
    # =========================================================================

    async def health_check(self) -> Dict:
        """Check database connections"""
        status = {
            "supabase": "disconnected",
            "mongodb": "disconnected"
        }
        
        # Check Supabase
        if self.supabase:
            if self._tables_exist:
                status["supabase"] = "connected"
            else:
                status["supabase"] = "connected (tables missing - run SCHEMA_SQL)"
        
        # Check MongoDB
        if self.mongo_db is not None:
            try:
                await self.mongo_db.command("ping")
                status["mongodb"] = "connected"
            except Exception as e:
                status["mongodb"] = f"error: {str(e)[:50]}"
        
        return status

    def get_schema_sql(self) -> str:
        """Return the schema SQL for manual execution"""
        return SCHEMA_SQL


# Global instance
lithium_db = LithiumDatabase()
