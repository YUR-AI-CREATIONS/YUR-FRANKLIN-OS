import os
import logging
from typing import Any, Dict, List
from supabase import create_client, Client

logger = logging.getLogger(__name__)
_client: Client = None


def get_supabase() -> Client:
    """Lazily initialize Supabase client using service role if available."""
    global _client
    if _client:
        return _client
    url = os.getenv("SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
    )
    if not url or not key:
        logger.info("Supabase not configured (missing SUPABASE_URL or key)")
        return None
    try:
        _client = create_client(url, key)
        logger.info("Supabase client initialized for %s", url)
    except Exception as e:
        logger.error("Failed to init Supabase: %s", e)
        _client = None
    return _client


def safe_upsert(table: str, rows: List[Dict[str, Any]]):
    sb = get_supabase()
    if not sb or not rows:
        return
    try:
        sb.table(table).upsert(rows).execute()
    except Exception as e:
        logger.warning("Supabase upsert failed (%s): %s", table, e)


def table_has_rows(table: str) -> bool:
    sb = get_supabase()
    if not sb:
        return False
    try:
        res = sb.table(table).select("id").limit(1).execute()
        return bool(res.data)
    except Exception as e:
        logger.warning("Supabase check failed (%s): %s", table, e)
        return False


def upsert_build_record(build: Dict[str, Any], project_id: str = None, mission: str = None):
    sb = get_supabase()
    if not sb:
        return
    try:
        sb.table("builds_supabase").upsert({
            "build_id": build.get("build_id") or build.get("id"),
            "project_id": project_id or build.get("project_id"),
            "mission": mission or build.get("mission"),
            "status": build.get("status") or "completed",
            "file_count": build.get("file_count") or build.get("stats", {}).get("files_created"),
            "total_lines": build.get("total_lines") or build.get("stats", {}).get("total_lines"),
            "completed_at": build.get("completed_at"),
            "agent_id": build.get("agent_id"),
            "contract": build.get("contract")
        }).execute()
    except Exception as e:
        logger.warning("Supabase build upsert failed: %s", e)


def upsert_artifacts(build_id: str, files: List[Dict[str, Any]]):
    sb = get_supabase()
    if not sb:
        return
    try:
        sb.table("artifacts_supabase").upsert({
            "build_id": build_id,
            "files": files,
            "file_count": len(files)
        }).execute()
    except Exception as e:
        logger.warning("Supabase artifacts upsert failed: %s", e)


def upsert_certification(build_id: str, cert: Dict[str, Any]):
    sb = get_supabase()
    if not sb or not cert:
        return
    try:
        sb.table("certifications_supabase").upsert({
            "build_id": build_id,
            "all_gates_passed": cert.get("all_gates_passed"),
            "certification_hash": cert.get("certification_hash"),
            "certified_at": cert.get("certified_at"),
            "gates": cert.get("gates")
        }).execute()
    except Exception as e:
        logger.warning("Supabase cert upsert failed: %s", e)


# ============================================================================
#                        USER AUTHENTICATION
# ============================================================================

async def sign_up_user(email: str, password: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Sign up a new user"""
    sb = get_supabase()
    if not sb:
        raise Exception("Supabase not configured")
    try:
        response = sb.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata or {}
            }
        })
        return {
            "user": response.user,
            "session": response.session
        }
    except Exception as e:
        logger.error("Sign up failed: %s", e)
        raise

async def sign_in_user(email: str, password: str) -> Dict[str, Any]:
    """Sign in a user"""
    sb = get_supabase()
    if not sb:
        raise Exception("Supabase not configured")
    try:
        response = sb.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {
            "user": response.user,
            "session": response.session
        }
    except Exception as e:
        logger.error("Sign in failed: %s", e)
        raise

async def sign_out_user():
    """Sign out current user"""
    sb = get_supabase()
    if not sb:
        return
    try:
        sb.auth.sign_out()
    except Exception as e:
        logger.error("Sign out failed: %s", e)

def get_current_user():
    """Get current authenticated user"""
    sb = get_supabase()
    if not sb:
        return None
    try:
        return sb.auth.get_user()
    except Exception as e:
        logger.error("Get user failed: %s", e)
        return None

# ============================================================================
#                        PROJECT MANAGEMENT
# ============================================================================

async def create_project(name: str, description: str, user_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a new project"""
    sb = get_supabase()
    if not sb:
        raise Exception("Supabase not configured")
    try:
        response = sb.table("projects").insert({
            "name": name,
            "description": description,
            "user_id": user_id,
            "metadata": metadata or {},
            "created_at": "now()",
            "updated_at": "now()"
        }).execute()
        return response.data[0]
    except Exception as e:
        logger.error("Create project failed: %s", e)
        raise

async def get_user_projects(user_id: str) -> List[Dict[str, Any]]:
    """Get all projects for a user"""
    sb = get_supabase()
    if not sb:
        return []
    try:
        response = sb.table("projects").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        logger.error("Get projects failed: %s", e)
        return []

async def get_project(project_id: str) -> Dict[str, Any]:
    """Get a specific project"""
    sb = get_supabase()
    if not sb:
        return None
    try:
        response = sb.table("projects").select("*").eq("id", project_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error("Get project failed: %s", e)
        return None

async def update_project(project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update a project"""
    sb = get_supabase()
    if not sb:
        raise Exception("Supabase not configured")
    try:
        updates["updated_at"] = "now()"
        response = sb.table("projects").update(updates).eq("id", project_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error("Update project failed: %s", e)
        raise

async def delete_project(project_id: str):
    """Delete a project"""
    sb = get_supabase()
    if not sb:
        return
    try:
        sb.table("projects").delete().eq("id", project_id).execute()
    except Exception as e:
        logger.error("Delete project failed: %s", e)

# ============================================================================
#                        CERTIFICATION STORAGE
# ============================================================================

async def store_certification(project_id: str, certification: Dict[str, Any]) -> Dict[str, Any]:
    """Store certification data"""
    sb = get_supabase()
    if not sb:
        raise Exception("Supabase not configured")
    try:
        response = sb.table("certifications").insert({
            "project_id": project_id,
            "certification_data": certification,
            "created_at": "now()"
        }).execute()
        return response.data[0]
    except Exception as e:
        logger.error("Store certification failed: %s", e)
        raise

async def get_project_certifications(project_id: str) -> List[Dict[str, Any]]:
    """Get certifications for a project"""
    sb = get_supabase()
    if not sb:
        return []
    try:
        response = sb.table("certifications").select("*").eq("project_id", project_id).execute()
        return response.data
    except Exception as e:
        logger.error("Get certifications failed: %s", e)
        return []
