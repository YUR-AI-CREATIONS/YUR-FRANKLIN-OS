"""
LITHIUM DATABASE MANAGER
Direct PostgreSQL (Supabase) + MongoDB dual-layer persistence
"""

import os
import asyncpg
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


# ============================================================================
# SCHEMA SQL - Run this in Supabase SQL Editor if tables don't exist
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

-- BUILDS TABLE
CREATE TABLE IF NOT EXISTS builds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
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

-- PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_session_id VARCHAR(255),
    stripe_payment_intent VARCHAR(255),
    amount_cents INTEGER,
    currency VARCHAR(10) DEFAULT 'usd',
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_builds_build_id ON builds(build_id);
CREATE INDEX IF NOT EXISTS idx_certifications_build_id ON certifications(build_id);
"""


class LithiumDatabase:
    """
    Dual-layer database manager:
    - PostgreSQL (Supabase) for structured data
    - MongoDB for documents and file contents
    """

    def __init__(self):
        # PostgreSQL (Supabase)
        self.pg_url = os.getenv("SUPABASE_DB_URL")
        self.pg_pool: Optional[asyncpg.Pool] = None
        
        # MongoDB
        self.mongo_url = os.getenv("MONGO_URL")
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.mongo_db = None
        
        self._initialized = False

    async def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
        
        # Connect to PostgreSQL
        if self.pg_url and "[YOUR-PASSWORD]" not in self.pg_url:
            try:
                self.pg_pool = await asyncpg.create_pool(
                    self.pg_url,
                    min_size=2,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("✓ PostgreSQL (Supabase) connected")
                
                # Try to create tables
                await self._ensure_tables()
            except Exception as e:
                logger.error(f"✗ PostgreSQL connection failed: {e}")
                self.pg_pool = None
        else:
            logger.warning("PostgreSQL URL not configured or password not set")
        
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

    async def _ensure_tables(self):
        """Create tables if they don't exist"""
        if self.pg_pool is None:
            return
            
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute(SCHEMA_SQL)
                logger.info("✓ PostgreSQL tables ensured")
        except Exception as e:
            logger.warning(f"Table creation warning: {e}")

    # =========================================================================
    # BUILD OPERATIONS
    # =========================================================================

    async def save_build(self, build_data: Dict) -> Optional[Dict]:
        """Save a build to both PostgreSQL and MongoDB"""
        saved_pg = False
        saved_mongo = False
        
        build_id = build_data["build_id"]
        
        # Save to PostgreSQL (structured data)
        if self.pg_pool is not None:
            try:
                async with self.pg_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO builds (build_id, mission, tech_stack, status, files_count, total_lines, total_bytes, tree, completed_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (build_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            completed_at = EXCLUDED.completed_at
                    """,
                        build_id,
                        build_data.get("prompt", build_data.get("mission", "")),
                        build_data.get("tech_stack"),
                        build_data.get("status", "completed"),
                        build_data.get("stats", {}).get("files_created", 0),
                        build_data.get("stats", {}).get("total_lines", 0),
                        build_data.get("stats", {}).get("total_bytes", 0),
                        build_data.get("tree"),
                        datetime.now(timezone.utc) if build_data.get("status") == "completed" else None
                    )
                saved_pg = True
                logger.info(f"Build {build_id} saved to PostgreSQL")
            except Exception as e:
                logger.error(f"PostgreSQL save failed: {e}")
        
        # Save to MongoDB (file contents)
        if self.mongo_db is not None:
            try:
                doc = {
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
                    {"$set": doc},
                    upsert=True
                )
                saved_mongo = True
                logger.info(f"Build {build_id} saved to MongoDB")
            except Exception as e:
                logger.error(f"MongoDB save failed: {e}")
        
        return build_data if (saved_pg or saved_mongo) else None

    async def get_build(self, build_id: str) -> Optional[Dict]:
        """Get a build by ID"""
        build = None
        
        # Try PostgreSQL first for metadata
        if self.pg_pool is not None:
            try:
                async with self.pg_pool.acquire() as conn:
                    row = await conn.fetchrow(
                        "SELECT * FROM builds WHERE build_id = $1", build_id
                    )
                    if row:
                        build = dict(row)
            except Exception as e:
                logger.error(f"PostgreSQL get_build failed: {e}")
        
        # Get file contents from MongoDB
        if self.mongo_db is not None:
            try:
                mongo_doc = await self.mongo_db.builds.find_one({"build_id": build_id})
                if mongo_doc:
                    if build:
                        build["file_contents"] = mongo_doc.get("file_contents", {})
                    else:
                        build = {
                            "build_id": mongo_doc.get("build_id"),
                            "mission": mongo_doc.get("mission"),
                            "tech_stack": mongo_doc.get("tech_stack"),
                            "status": mongo_doc.get("status"),
                            "file_contents": mongo_doc.get("file_contents", {})
                        }
            except Exception as e:
                logger.error(f"MongoDB get_build failed: {e}")
        
        return build

    async def get_recent_builds(self, limit: int = 20) -> List[Dict]:
        """Get recent builds"""
        builds = []
        
        if self.pg_pool is not None:
            try:
                async with self.pg_pool.acquire() as conn:
                    rows = await conn.fetch(
                        "SELECT build_id, mission, tech_stack, status, files_count, total_lines, created_at FROM builds ORDER BY created_at DESC LIMIT $1",
                        limit
                    )
                    builds = [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"PostgreSQL get_recent_builds failed: {e}")
        
        # Fallback to MongoDB
        if not builds and self.mongo_db is not None:
            try:
                cursor = self.mongo_db.builds.find().sort("created_at", -1).limit(limit)
                async for doc in cursor:
                    builds.append({
                        "build_id": doc.get("build_id"),
                        "mission": doc.get("mission"),
                        "tech_stack": doc.get("tech_stack"),
                        "status": doc.get("status"),
                        "files_count": doc.get("files_count"),
                        "total_lines": doc.get("total_lines"),
                        "created_at": doc.get("created_at")
                    })
            except Exception as e:
                logger.error(f"MongoDB get_recent_builds failed: {e}")
        
        return builds

    # =========================================================================
    # CERTIFICATION OPERATIONS
    # =========================================================================

    async def save_certification(self, cert_data: Dict) -> Optional[Dict]:
        """Save certification results"""
        build_id = cert_data["build_id"]
        
        if self.pg_pool is not None:
            try:
                async with self.pg_pool.acquire() as conn:
                    import json
                    await conn.execute("""
                        INSERT INTO certifications (build_id, certification_hash, total_score, passed_gates, failed_gates, all_passed, gate_results, certified_at, signed_by)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                        build_id,
                        cert_data.get("certification_hash"),
                        cert_data.get("total_score", 0),
                        cert_data.get("passed_gates", 0),
                        cert_data.get("failed_gates", 0),
                        cert_data.get("all_passed", False),
                        json.dumps(cert_data.get("gates", [])),
                        datetime.now(timezone.utc) if cert_data.get("all_passed") else None,
                        cert_data.get("signed_by", "FRANKLIN")
                    )
                logger.info(f"Certification for {build_id} saved to PostgreSQL")
                return cert_data
            except Exception as e:
                logger.error(f"PostgreSQL save_certification failed: {e}")
        
        # Fallback to MongoDB
        if self.mongo_db is not None:
            try:
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
        if self.pg_pool is not None:
            try:
                async with self.pg_pool.acquire() as conn:
                    row = await conn.fetchrow(
                        "SELECT * FROM certifications WHERE build_id = $1 ORDER BY certified_at DESC LIMIT 1",
                        build_id
                    )
                    if row:
                        return dict(row)
            except Exception as e:
                logger.error(f"PostgreSQL get_certification failed: {e}")
        
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
            "postgresql": "disconnected",
            "mongodb": "disconnected"
        }
        
        if self.pg_pool is not None:
            try:
                async with self.pg_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                status["postgresql"] = "connected"
            except Exception as e:
                status["postgresql"] = f"error: {str(e)[:50]}"
        
        if self.mongo_db is not None:
            try:
                await self.mongo_db.command("ping")
                status["mongodb"] = "connected"
            except Exception as e:
                status["mongodb"] = f"error: {str(e)[:50]}"
        
        return status


# Global instance
lithium_db = LithiumDatabase()
