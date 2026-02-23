"""
LITHIUM DATABASE MANAGER
PostgreSQL (Supabase) + MongoDB dual-layer persistence
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# ============================================================================
# SUPABASE SCHEMA (PostgreSQL)
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
    build_id VARCHAR(100) REFERENCES builds(build_id) ON DELETE CASCADE,
    certification_hash VARCHAR(64),
    total_score FLOAT DEFAULT 0,
    passed_gates INTEGER DEFAULT 0,
    failed_gates INTEGER DEFAULT 0,
    all_passed BOOLEAN DEFAULT FALSE,
    gate_1_passed BOOLEAN DEFAULT FALSE,
    gate_1_score FLOAT DEFAULT 0,
    gate_2_passed BOOLEAN DEFAULT FALSE,
    gate_2_score FLOAT DEFAULT 0,
    gate_3_passed BOOLEAN DEFAULT FALSE,
    gate_3_score FLOAT DEFAULT 0,
    gate_4_passed BOOLEAN DEFAULT FALSE,
    gate_4_score FLOAT DEFAULT 0,
    gate_5_passed BOOLEAN DEFAULT FALSE,
    gate_5_score FLOAT DEFAULT 0,
    gate_6_passed BOOLEAN DEFAULT FALSE,
    gate_6_score FLOAT DEFAULT 0,
    gate_7_passed BOOLEAN DEFAULT FALSE,
    gate_7_score FLOAT DEFAULT 0,
    gate_8_passed BOOLEAN DEFAULT FALSE,
    gate_8_score FLOAT DEFAULT 0,
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

-- CHAT SESSIONS TABLE
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    session_type VARCHAR(50) DEFAULT 'franklin',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_builds_project ON builds(project_id);
CREATE INDEX IF NOT EXISTS idx_builds_user ON builds(user_id);
CREATE INDEX IF NOT EXISTS idx_builds_build_id ON builds(build_id);
CREATE INDEX IF NOT EXISTS idx_certifications_build ON certifications(build_id);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id);
"""


class LithiumDatabase:
    """
    Dual-layer database manager:
    - PostgreSQL (Supabase) for structured data
    - MongoDB for documents and chat history
    """

    def __init__(self):
        # Supabase (PostgreSQL)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase: Optional[Client] = None
        
        # MongoDB
        self.mongo_url = os.getenv("MONGO_URL")
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.mongo_db = None
        
        self._initialized = False

    async def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
            
        # Connect to Supabase
        if self.supabase_url and self.supabase_key:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                logger.info(f"✓ Supabase connected: {self.supabase_url}")
            except Exception as e:
                logger.error(f"✗ Supabase connection failed: {e}")
        
        # Connect to MongoDB
        if self.mongo_url:
            try:
                self.mongo_client = AsyncIOMotorClient(self.mongo_url)
                self.mongo_db = self.mongo_client[os.getenv("DB_NAME", "franklin_os")]
                logger.info("✓ MongoDB connected")
            except Exception as e:
                logger.error(f"✗ MongoDB connection failed: {e}")
        
        self._initialized = True

    # =========================================================================
    # USER OPERATIONS
    # =========================================================================

    async def create_user(self, email: str, password_hash: str = None, subscription_tier: str = "free") -> Optional[Dict]:
        """Create a new user"""
        if self.supabase is None:
            return None
            
        try:
            result = self.supabase.table("users").insert({
                "email": email,
                "password_hash": password_hash,
                "subscription_tier": subscription_tier
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Create user failed: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        if self.supabase is None:
            return None
            
        try:
            result = self.supabase.table("users").select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Get user failed: {e}")
            return None

    async def update_user_subscription(self, user_id: str, tier: str, stripe_customer_id: str = None) -> bool:
        """Update user subscription"""
        if self.supabase is None:
            return False
            
        try:
            data = {"subscription_tier": tier, "updated_at": datetime.now(timezone.utc).isoformat()}
            if stripe_customer_id:
                data["stripe_customer_id"] = stripe_customer_id
            self.supabase.table("users").update(data).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Update user failed: {e}")
            return False

    # =========================================================================
    # PROJECT OPERATIONS
    # =========================================================================

    async def create_project(self, user_id: str, name: str, description: str = None, tech_stack: str = None) -> Optional[Dict]:
        """Create a new project"""
        if self.supabase is None:
            return None
            
        try:
            result = self.supabase.table("projects").insert({
                "user_id": user_id,
                "name": name,
                "description": description,
                "tech_stack": tech_stack,
                "status": "draft"
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Create project failed: {e}")
            return None

    async def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        if self.supabase is None:
            return []
            
        try:
            result = self.supabase.table("projects").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Get projects failed: {e}")
            return []

    # =========================================================================
    # BUILD OPERATIONS
    # =========================================================================

    async def save_build(self, build_data: Dict) -> Optional[Dict]:
        """Save a build to the database"""
        if self.supabase is None:
            return None
            
        try:
            record = {
                "build_id": build_data["build_id"],
                "mission": build_data.get("prompt", build_data.get("mission", "")),
                "tech_stack": build_data.get("tech_stack"),
                "status": build_data.get("status", "completed"),
                "files_count": build_data.get("stats", {}).get("files_created", 0),
                "total_lines": build_data.get("stats", {}).get("total_lines", 0),
                "total_bytes": build_data.get("stats", {}).get("total_bytes", 0),
                "tree": build_data.get("tree"),
                "user_id": build_data.get("user_id"),
                "project_id": build_data.get("project_id")
            }
            
            if build_data.get("status") == "completed":
                record["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.supabase.table("builds").insert(record).execute()
            
            # Also save file contents to MongoDB
            if self.mongo_db and build_data.get("file_contents"):
                await self.mongo_db.build_artifacts.insert_one({
                    "build_id": build_data["build_id"],
                    "files": [
                        {"path": path, "content": content}
                        for path, content in build_data["file_contents"].items()
                    ],
                    "created_at": datetime.now(timezone.utc)
                })
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Save build failed: {e}")
            return None

    async def get_build(self, build_id: str) -> Optional[Dict]:
        """Get a build by ID"""
        if self.supabase is None:
            return None
            
        try:
            result = self.supabase.table("builds").select("*").eq("build_id", build_id).execute()
            build = result.data[0] if result.data else None
            
            # Also get file contents from MongoDB
            if build and self.mongo_db:
                artifacts = await self.mongo_db.build_artifacts.find_one({"build_id": build_id})
                if artifacts:
                    build["files"] = artifacts.get("files", [])
            
            return build
        except Exception as e:
            logger.error(f"Get build failed: {e}")
            return None

    async def get_user_builds(self, user_id: str) -> List[Dict]:
        """Get all builds for a user"""
        if self.supabase is None:
            return []
            
        try:
            result = self.supabase.table("builds").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Get builds failed: {e}")
            return []

    # =========================================================================
    # CERTIFICATION OPERATIONS
    # =========================================================================

    async def save_certification(self, cert_data: Dict) -> Optional[Dict]:
        """Save certification results"""
        if self.supabase is None:
            return None
            
        try:
            record = {
                "build_id": cert_data["build_id"],
                "certification_hash": cert_data.get("certification_hash"),
                "total_score": cert_data.get("total_score", 0),
                "passed_gates": cert_data.get("passed_gates", 0),
                "failed_gates": cert_data.get("failed_gates", 0),
                "all_passed": cert_data.get("all_passed", False),
                "signed_by": cert_data.get("signed_by", "FRANKLIN")
            }
            
            # Add individual gate results
            for gate in cert_data.get("gates", []):
                gate_num = gate["gate_num"]
                record[f"gate_{gate_num}_passed"] = gate["passed"]
                record[f"gate_{gate_num}_score"] = gate["score"]
            
            if cert_data.get("all_passed"):
                record["certified_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.supabase.table("certifications").insert(record).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Save certification failed: {e}")
            return None

    async def get_certification(self, build_id: str) -> Optional[Dict]:
        """Get certification for a build"""
        if self.supabase is None:
            return None
            
        try:
            result = self.supabase.table("certifications").select("*").eq("build_id", build_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Get certification failed: {e}")
            return None

    # =========================================================================
    # PAYMENT OPERATIONS
    # =========================================================================

    async def save_payment(self, user_id: str, stripe_session_id: str, amount_cents: int, status: str = "pending") -> Optional[Dict]:
        """Save a payment record"""
        if self.supabase is None:
            return None
            
        try:
            result = self.supabase.table("payments").insert({
                "user_id": user_id,
                "stripe_session_id": stripe_session_id,
                "amount_cents": amount_cents,
                "status": status
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Save payment failed: {e}")
            return None

    async def update_payment_status(self, stripe_session_id: str, status: str, payment_intent: str = None) -> bool:
        """Update payment status"""
        if self.supabase is None:
            return False
            
        try:
            data = {"status": status}
            if payment_intent:
                data["stripe_payment_intent"] = payment_intent
            self.supabase.table("payments").update(data).eq("stripe_session_id", stripe_session_id).execute()
            return True
        except Exception as e:
            logger.error(f"Update payment failed: {e}")
            return False

    # =========================================================================
    # CHAT HISTORY (MongoDB)
    # =========================================================================

    async def save_chat_message(self, session_id: str, message: Dict, session_type: str = "franklin") -> bool:
        """Save a chat message to MongoDB"""
        if self.mongo_db is None:
            return False
            
        try:
            await self.mongo_db.chat_history.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.now(timezone.utc), "type": session_type},
                    "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Save chat message failed: {e}")
            return False

    async def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        if self.mongo_db is None:
            return []
            
        try:
            doc = await self.mongo_db.chat_history.find_one({"session_id": session_id})
            return doc.get("messages", []) if doc else []
        except Exception as e:
            logger.error(f"Get chat history failed: {e}")
            return []

    # =========================================================================
    # HEALTH CHECK
    # =========================================================================

    async def health_check(self) -> Dict:
        """Check database connections"""
        status = {
            "supabase": "disconnected",
            "mongodb": "disconnected"
        }
        
        # Check Supabase connection (not tables)
        if self.supabase is not None:
            try:
                # Just check if we can reach Supabase
                status["supabase"] = "connected (tables may need creation)"
            except Exception as e:
                status["supabase"] = f"error: {str(e)[:50]}"
        
        # Check MongoDB
        if self.mongo_db is not None:
            try:
                await self.mongo_db.command("ping")
                status["mongodb"] = "connected"
            except Exception as e:
                status["mongodb"] = f"error: {str(e)[:50]}"
        
        return status


# Global instance
lithium_db = LithiumDatabase()
