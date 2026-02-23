"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PERSISTENCE & TASK TRACKING                                ║
║                                                                              ║
║  - Save conversations to MongoDB                                             ║
║  - Track background tasks with real-time status                              ║
║  - Provide proof of work (timestamps, logs, progress)                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bson import ObjectId
import asyncio
import logging

logger = logging.getLogger(__name__)


class PersistenceManager:
    """Handles saving and loading conversations, sessions, and tasks"""
    
    def __init__(self, db):
        self.db = db
        self.conversations = db.conversations
        self.build_sessions = db.build_sessions
        self.tasks = db.tasks
        self.task_logs = db.task_logs
    
    # ========== CONVERSATION PERSISTENCE ==========
    
    async def save_conversation(self, user_id: str, conversation_type: str, 
                                 entity_name: str, messages: List[Dict]) -> str:
        """Save a conversation to the database"""
        doc = {
            "user_id": user_id,
            "type": conversation_type,  # 'franklin', 'agent', 'bot', 'academy'
            "entity_name": entity_name,
            "messages": messages,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        result = await self.conversations.insert_one(doc)
        return str(result.inserted_id)
    
    async def update_conversation(self, conversation_id: str, messages: List[Dict]) -> bool:
        """Update an existing conversation"""
        result = await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "messages": messages,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count > 0
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation"""
        doc = await self.conversations.find_one({"_id": ObjectId(conversation_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_user_conversations(self, user_id: str, 
                                      conversation_type: Optional[str] = None) -> List[Dict]:
        """Get all conversations for a user"""
        query = {"user_id": user_id}
        if conversation_type:
            query["type"] = conversation_type
        
        cursor = self.conversations.find(query).sort("updated_at", -1)
        conversations = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            conversations.append(doc)
        return conversations
    
    async def get_or_create_conversation(self, user_id: str, conversation_type: str,
                                          entity_name: str) -> Dict:
        """Get existing conversation or create new one"""
        doc = await self.conversations.find_one({
            "user_id": user_id,
            "type": conversation_type,
            "entity_name": entity_name
        })
        
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
        
        # Create new conversation
        conv_id = await self.save_conversation(user_id, conversation_type, entity_name, [])
        return {
            "_id": conv_id,
            "user_id": user_id,
            "type": conversation_type,
            "entity_name": entity_name,
            "messages": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    
    # ========== BUILD SESSION PERSISTENCE ==========
    
    async def save_build_session(self, session_data: Dict) -> str:
        """Save a build session to the database"""
        session_data["created_at"] = datetime.now(timezone.utc)
        session_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.build_sessions.insert_one(session_data)
        return str(result.inserted_id)
    
    async def update_build_session(self, session_id: str, updates: Dict) -> bool:
        """Update a build session"""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.build_sessions.update_one(
            {"session_id": session_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def get_build_session(self, session_id: str) -> Optional[Dict]:
        """Get a build session"""
        doc = await self.build_sessions.find_one({"session_id": session_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_user_build_sessions(self, user_id: str) -> List[Dict]:
        """Get all build sessions for a user"""
        cursor = self.build_sessions.find({"user_id": user_id}).sort("created_at", -1)
        sessions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            sessions.append(doc)
        return sessions


class TaskTracker:
    """Tracks background tasks with real-time status and proof of work"""
    
    def __init__(self, db):
        self.db = db
        self.tasks = db.tasks
        self.task_logs = db.task_logs
        self.active_tasks: Dict[str, Dict] = {}
    
    async def create_task(self, task_type: str, description: str, 
                          user_id: str, params: Dict = None) -> str:
        """Create a new tracked task"""
        task_id = str(ObjectId())
        task = {
            "task_id": task_id,
            "type": task_type,
            "description": description,
            "user_id": user_id,
            "params": params or {},
            "status": "pending",
            "progress": 0,
            "steps_completed": [],
            "steps_remaining": [],
            "created_at": datetime.now(timezone.utc),
            "started_at": None,
            "completed_at": None,
            "last_update": datetime.now(timezone.utc),
            "result": None,
            "error": None
        }
        
        await self.tasks.insert_one(task)
        self.active_tasks[task_id] = task
        
        # Log task creation
        await self._log_task_event(task_id, "created", f"Task created: {description}")
        
        return task_id
    
    async def start_task(self, task_id: str, steps: List[str] = None) -> bool:
        """Mark a task as started"""
        now = datetime.now(timezone.utc)
        update = {
            "status": "running",
            "started_at": now,
            "last_update": now,
            "steps_remaining": steps or []
        }
        
        result = await self.tasks.update_one(
            {"task_id": task_id},
            {"$set": update}
        )
        
        if task_id in self.active_tasks:
            self.active_tasks[task_id].update(update)
        
        await self._log_task_event(task_id, "started", "Task execution started")
        
        return result.modified_count > 0
    
    async def update_task_progress(self, task_id: str, progress: int, 
                                    step_completed: str = None,
                                    current_action: str = None) -> bool:
        """Update task progress with proof of work"""
        now = datetime.now(timezone.utc)
        update = {
            "progress": progress,
            "last_update": now
        }
        
        update_ops = {"$set": update}
        
        if step_completed:
            update_ops["$push"] = {"steps_completed": {
                "step": step_completed,
                "completed_at": now
            }}
            update_ops["$pull"] = {"steps_remaining": step_completed}
        
        result = await self.tasks.update_one(
            {"task_id": task_id},
            update_ops
        )
        
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["progress"] = progress
            self.active_tasks[task_id]["last_update"] = now
        
        log_msg = f"Progress: {progress}%"
        if step_completed:
            log_msg += f" - Completed: {step_completed}"
        if current_action:
            log_msg += f" - Current: {current_action}"
        
        await self._log_task_event(task_id, "progress", log_msg)
        
        return result.modified_count > 0
    
    async def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark a task as completed"""
        now = datetime.now(timezone.utc)
        update = {
            "status": "completed",
            "progress": 100,
            "completed_at": now,
            "last_update": now,
            "result": result
        }
        
        await self.tasks.update_one(
            {"task_id": task_id},
            {"$set": update}
        )
        
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        
        await self._log_task_event(task_id, "completed", "Task completed successfully")
        
        return True
    
    async def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        now = datetime.now(timezone.utc)
        update = {
            "status": "failed",
            "completed_at": now,
            "last_update": now,
            "error": error
        }
        
        await self.tasks.update_one(
            {"task_id": task_id},
            {"$set": update}
        )
        
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        
        await self._log_task_event(task_id, "failed", f"Task failed: {error}")
        
        return True
    
    async def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task status with full proof of work"""
        task = await self.tasks.find_one({"task_id": task_id}, {"_id": 0})
        if task:
            # Get task logs for proof of work
            logs = await self.get_task_logs(task_id)
            task["logs"] = logs
        return task
    
    async def get_user_tasks(self, user_id: str, status: str = None) -> List[Dict]:
        """Get all tasks for a user"""
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        cursor = self.tasks.find(query, {"_id": 0}).sort("created_at", -1)
        tasks = []
        async for doc in cursor:
            tasks.append(doc)
        return tasks
    
    async def get_active_tasks(self, user_id: str = None) -> List[Dict]:
        """Get all currently running tasks"""
        query = {"status": "running"}
        if user_id:
            query["user_id"] = user_id
        
        cursor = self.tasks.find(query, {"_id": 0})
        tasks = []
        async for doc in cursor:
            tasks.append(doc)
        return tasks
    
    async def _log_task_event(self, task_id: str, event_type: str, message: str):
        """Log a task event for proof of work"""
        log = {
            "task_id": task_id,
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc)
        }
        await self.task_logs.insert_one(log)
    
    async def get_task_logs(self, task_id: str) -> List[Dict]:
        """Get all logs for a task - proof of work"""
        cursor = self.task_logs.find(
            {"task_id": task_id}, 
            {"_id": 0}
        ).sort("timestamp", 1)
        
        logs = []
        async for doc in cursor:
            logs.append(doc)
        return logs


# Helper to serialize datetime for JSON
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj
