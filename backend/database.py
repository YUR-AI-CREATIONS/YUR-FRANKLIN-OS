"""
LITHIUM DATABASE LAYER
Real database connections - no mocking, no faking
"""

import os
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from uuid import uuid4
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SUPABASE/POSTGRESQL CONNECTION
# ============================================================================

class PostgresDB:
    """Direct PostgreSQL connection to Supabase"""
    
    def __init__(self):
        self.database_url = os.environ.get("DIRECT_URL")
        self.pool: Optional[asyncpg.Pool] = None
        self._initialized = False
    
    async def connect(self):
        """Establish connection pool"""
        if self._initialized:
            return
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            self._initialized = True
            logger.info("✓ PostgreSQL connected")
        except Exception as e:
            logger.error(f"✗ PostgreSQL connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self._initialized = False
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query"""
        if not self._initialized:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        """Fetch multiple rows"""
        if not self._initialized:
            await self.connect()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row"""
        if not self._initialized:
            await self.connect()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetchval(self, query: str, *args):
        """Fetch single value"""
        if not self._initialized:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# ============================================================================
# MONGODB CONNECTION
# ============================================================================

class MongoDB:
    """MongoDB for documents, artifacts, logs"""
    
    def __init__(self):
        self.mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = os.environ.get("DB_NAME", "franklin_os")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._initialized = False
    
    async def connect(self):
        """Establish MongoDB connection"""
        if self._initialized:
            return
        
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            # Test connection
            await self.client.admin.command('ping')
            self._initialized = True
            logger.info("✓ MongoDB connected")
        except Exception as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._initialized = False
    
    # Collections
    @property
    def chat_history(self):
        return self.db["chat_history"]
    
    @property
    def build_artifacts(self):
        return self.db["build_artifacts"]
    
    @property
    def terminal_logs(self):
        return self.db["terminal_logs"]


# ============================================================================
# DATABASE SCHEMA INITIALIZATION
# ============================================================================

SCHEMA_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Builds table
CREATE TABLE IF NOT EXISTS builds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    mission TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    spec_content TEXT,
    architecture_content TEXT,
    code_content TEXT,
    health_report TEXT,
    artifacts_path VARCHAR(500),
    file_count INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Certifications table
CREATE TABLE IF NOT EXISTS certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    build_id UUID REFERENCES builds(id) ON DELETE CASCADE,
    certification_hash VARCHAR(64) NOT NULL,
    gate_1_passed BOOLEAN DEFAULT FALSE,
    gate_1_details JSONB,
    gate_2_passed BOOLEAN DEFAULT FALSE,
    gate_2_details JSONB,
    gate_3_passed BOOLEAN DEFAULT FALSE,
    gate_3_details JSONB,
    gate_4_passed BOOLEAN DEFAULT FALSE,
    gate_4_details JSONB,
    gate_5_passed BOOLEAN DEFAULT FALSE,
    gate_5_details JSONB,
    gate_6_passed BOOLEAN DEFAULT FALSE,
    gate_6_details JSONB,
    gate_7_passed BOOLEAN DEFAULT FALSE,
    gate_7_details JSONB,
    gate_8_passed BOOLEAN DEFAULT FALSE,
    gate_8_details JSONB,
    all_gates_passed BOOLEAN DEFAULT FALSE,
    certified_at TIMESTAMPTZ,
    signed_by VARCHAR(100) DEFAULT 'FRANKLIN'
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    stripe_session_id VARCHAR(255),
    stripe_payment_intent VARCHAR(255),
    amount_cents INTEGER,
    currency VARCHAR(10) DEFAULT 'usd',
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_builds_project ON builds(project_id);
CREATE INDEX IF NOT EXISTS idx_builds_user ON builds(user_id);
CREATE INDEX IF NOT EXISTS idx_builds_status ON builds(status);
CREATE INDEX IF NOT EXISTS idx_certifications_build ON certifications(build_id);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
"""


# ============================================================================
# UNIFIED DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """
    Unified database manager for Franklin OS
    Handles both PostgreSQL (Supabase) and MongoDB
    Falls back to MongoDB-only if PostgreSQL unavailable
    """
    
    def __init__(self):
        self.pg = PostgresDB()
        self.mongo = MongoDB()
        self._schema_initialized = False
        self._pg_available = False
    
    async def initialize(self):
        """Initialize all database connections and schema"""
        # Always connect MongoDB (local, reliable)
        await self.mongo.connect()
        
        # Try PostgreSQL but don't fail if unavailable
        try:
            await self.pg.connect()
            self._pg_available = True
            if not self._schema_initialized:
                await self._init_schema()
                self._schema_initialized = True
            logger.info("✓ PostgreSQL connected")
        except Exception as e:
            logger.warning(f"PostgreSQL unavailable, using MongoDB only: {e}")
            self._pg_available = False
        
        logger.info(f"✓ Database layer initialized (PG: {self._pg_available}, Mongo: True)")
    
    async def _init_schema(self):
        """Create tables if they don't exist"""
        if not self._pg_available:
            return
        try:
            # Split and execute each statement
            for statement in SCHEMA_SQL.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    await self.pg.execute(statement)
            logger.info("✓ PostgreSQL schema initialized")
        except Exception as e:
            logger.warning(f"Schema init warning (may already exist): {e}")
    
    async def shutdown(self):
        """Close all connections"""
        await self.pg.disconnect()
        await self.mongo.disconnect()
    
    # ========================================================================
    # USER OPERATIONS
    # ========================================================================
    
    async def create_user(self, email: str, password_hash: str = None) -> Dict:
        """Create a new user"""
        user_id = str(uuid4())
        await self.pg.execute(
            """INSERT INTO users (id, email, password_hash) VALUES ($1, $2, $3)""",
            user_id, email, password_hash
        )
        return {"id": user_id, "email": email}
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return await self.pg.fetchrow(
            """SELECT id, email, subscription_tier, created_at FROM users WHERE email = $1""",
            email
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return await self.pg.fetchrow(
            """SELECT id, email, subscription_tier, created_at FROM users WHERE id = $1::uuid""",
            user_id
        )
    
    # ========================================================================
    # PROJECT OPERATIONS
    # ========================================================================
    
    async def create_project(self, user_id: str, name: str, description: str = "") -> Dict:
        """Create a new project"""
        project_id = str(uuid4())
        await self.pg.execute(
            """INSERT INTO projects (id, user_id, name, description) VALUES ($1, $2::uuid, $3, $4)""",
            project_id, user_id, name, description
        )
        return {"id": project_id, "name": name}
    
    async def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        return await self.pg.fetch(
            """SELECT id, name, description, status, created_at FROM projects WHERE user_id = $1::uuid ORDER BY created_at DESC""",
            user_id
        )
    
    # ========================================================================
    # BUILD OPERATIONS
    # ========================================================================
    
    async def create_build(self, mission: str, user_id: str = None, project_id: str = None) -> Dict:
        """Create a new build record"""
        build_id = str(uuid4())
        await self.pg.execute(
            """INSERT INTO builds (id, mission, user_id, project_id, status) 
               VALUES ($1, $2, $3::uuid, $4::uuid, 'building')""",
            build_id, mission, user_id, project_id
        )
        return {"id": build_id, "mission": mission, "status": "building"}
    
    async def update_build(self, build_id: str, **kwargs) -> None:
        """Update build fields"""
        allowed = ['status', 'spec_content', 'architecture_content', 'code_content', 
                   'health_report', 'artifacts_path', 'file_count', 'total_lines', 'completed_at']
        
        updates = []
        values = []
        idx = 1
        
        for key, value in kwargs.items():
            if key in allowed:
                updates.append(f"{key} = ${idx}")
                values.append(value)
                idx += 1
        
        if updates:
            values.append(build_id)
            query = f"UPDATE builds SET {', '.join(updates)} WHERE id = ${idx}::uuid"
            await self.pg.execute(query, *values)
    
    async def get_build(self, build_id: str) -> Optional[Dict]:
        """Get a build by ID"""
        return await self.pg.fetchrow(
            """SELECT * FROM builds WHERE id = $1::uuid""",
            build_id
        )
    
    async def get_user_builds(self, user_id: str) -> List[Dict]:
        """Get all builds for a user"""
        return await self.pg.fetch(
            """SELECT id, mission, status, file_count, total_lines, created_at, completed_at 
               FROM builds WHERE user_id = $1::uuid ORDER BY created_at DESC""",
            user_id
        )
    
    async def get_pending_certification_builds(self) -> List[Dict]:
        """Get builds ready for certification"""
        return await self.pg.fetch(
            """SELECT b.* FROM builds b 
               LEFT JOIN certifications c ON c.build_id = b.id
               WHERE b.status = 'completed' AND c.id IS NULL
               ORDER BY b.completed_at DESC"""
        )
    
    # ========================================================================
    # CERTIFICATION OPERATIONS
    # ========================================================================
    
    async def create_certification(self, build_id: str) -> Dict:
        """Create a certification record for a build"""
        cert_id = str(uuid4())
        
        # Get build content for hashing
        build = await self.get_build(build_id)
        if not build:
            raise ValueError(f"Build {build_id} not found")
        
        # Generate certification hash
        content = f"{build.get('spec_content', '')}{build.get('architecture_content', '')}{build.get('code_content', '')}"
        cert_hash = hashlib.sha256(content.encode()).hexdigest()
        
        await self.pg.execute(
            """INSERT INTO certifications (id, build_id, certification_hash) VALUES ($1, $2::uuid, $3)""",
            cert_id, build_id, cert_hash
        )
        
        return {"id": cert_id, "build_id": build_id, "hash": cert_hash}
    
    async def update_gate(self, cert_id: str, gate_num: int, passed: bool, details: Dict) -> None:
        """Update a specific gate result"""
        if gate_num < 1 or gate_num > 8:
            raise ValueError("Gate number must be between 1 and 8")
        
        await self.pg.execute(
            f"""UPDATE certifications 
                SET gate_{gate_num}_passed = $1, gate_{gate_num}_details = $2
                WHERE id = $3::uuid""",
            passed, json.dumps(details), cert_id
        )
    
    async def finalize_certification(self, cert_id: str) -> Dict:
        """Check all gates and finalize certification"""
        cert = await self.pg.fetchrow(
            """SELECT * FROM certifications WHERE id = $1::uuid""",
            cert_id
        )
        
        if not cert:
            raise ValueError(f"Certification {cert_id} not found")
        
        # Check all gates
        all_passed = all([
            cert.get('gate_1_passed'),
            cert.get('gate_2_passed'),
            cert.get('gate_3_passed'),
            cert.get('gate_4_passed'),
            cert.get('gate_5_passed'),
            cert.get('gate_6_passed'),
            cert.get('gate_7_passed'),
            cert.get('gate_8_passed')
        ])
        
        if all_passed:
            await self.pg.execute(
                """UPDATE certifications 
                   SET all_gates_passed = TRUE, certified_at = NOW()
                   WHERE id = $1::uuid""",
                cert_id
            )
            
            # Update build status
            await self.pg.execute(
                """UPDATE builds SET status = 'certified' WHERE id = (
                    SELECT build_id FROM certifications WHERE id = $1::uuid
                )""",
                cert_id
            )
        
        return {
            "id": cert_id,
            "all_gates_passed": all_passed,
            "certified_at": datetime.now(timezone.utc).isoformat() if all_passed else None
        }
    
    async def get_certification(self, build_id: str) -> Optional[Dict]:
        """Get certification for a build"""
        row = await self.pg.fetchrow(
            """SELECT * FROM certifications WHERE build_id = $1::uuid""",
            build_id
        )
        if row:
            # Convert to dict and handle JSON fields
            result = dict(row)
            for i in range(1, 9):
                key = f'gate_{i}_details'
                if result.get(key) and isinstance(result[key], str):
                    result[key] = json.loads(result[key])
            return result
        return None
    
    # ========================================================================
    # MONGODB: ARTIFACTS OPERATIONS
    # ========================================================================
    
    async def save_build_artifacts(self, build_id: str, files: List[Dict]) -> str:
        """Save build artifacts to MongoDB"""
        await self.mongo.connect()
        
        doc = {
            "build_id": build_id,
            "files": files,
            "file_count": len(files),
            "total_lines": sum(f.get('content', '').count('\n') + 1 for f in files),
            "created_at": datetime.now(timezone.utc)
        }
        
        result = await self.mongo.build_artifacts.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_build_artifacts(self, build_id: str) -> Optional[Dict]:
        """Get build artifacts from MongoDB"""
        await self.mongo.connect()
        
        doc = await self.mongo.build_artifacts.find_one({"build_id": build_id})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    
    # ========================================================================
    # MONGODB: CHAT HISTORY OPERATIONS
    # ========================================================================
    
    async def save_chat_message(self, session_id: str, chat_type: str, role: str, content: str, user_id: str = None) -> None:
        """Save a chat message"""
        await self.mongo.connect()
        
        await self.mongo.chat_history.update_one(
            {"session_id": session_id, "type": chat_type},
            {
                "$push": {
                    "messages": {
                        "role": role,
                        "content": content,
                        "timestamp": datetime.now(timezone.utc)
                    }
                },
                "$set": {
                    "user_id": user_id,
                    "updated_at": datetime.now(timezone.utc)
                },
                "$setOnInsert": {
                    "created_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
    
    async def get_chat_history(self, session_id: str, chat_type: str) -> List[Dict]:
        """Get chat history for a session"""
        await self.mongo.connect()
        
        doc = await self.mongo.chat_history.find_one(
            {"session_id": session_id, "type": chat_type}
        )
        
        if doc:
            return doc.get("messages", [])
        return []
    
    # ========================================================================
    # MONGODB: TERMINAL LOGS
    # ========================================================================
    
    async def save_terminal_log(self, build_id: str, session_id: str, log_type: str, content: str) -> None:
        """Save terminal log entry"""
        await self.mongo.connect()
        
        await self.mongo.terminal_logs.update_one(
            {"build_id": build_id, "session_id": session_id},
            {
                "$push": {
                    "logs": {
                        "type": log_type,
                        "content": content,
                        "timestamp": datetime.now(timezone.utc)
                    }
                },
                "$set": {"updated_at": datetime.now(timezone.utc)},
                "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )
    
    async def get_terminal_logs(self, build_id: str) -> List[Dict]:
        """Get terminal logs for a build"""
        await self.mongo.connect()
        
        doc = await self.mongo.terminal_logs.find_one({"build_id": build_id})
        if doc:
            return doc.get("logs", [])
        return []


# Global instance
db = DatabaseManager()
