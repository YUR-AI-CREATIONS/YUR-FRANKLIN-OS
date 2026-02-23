"""
Simple in-memory realtime event broker for SSE streams.

This keeps lightweight per-project queues and lets routes push events
that frontend clients can consume via Server-Sent Events.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class RealtimeBroker:
    def __init__(self):
        # project_id -> list[asyncio.Queue]
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        self.lock = asyncio.Lock()

    async def subscribe(self, project_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        async with self.lock:
            self.subscribers.setdefault(project_id, []).append(queue)
        logger.debug("SSE subscribe %s (now %d)", project_id, len(self.subscribers.get(project_id, [])))
        return queue

    async def unsubscribe(self, project_id: str, queue: asyncio.Queue):
        async with self.lock:
            if project_id in self.subscribers:
                self.subscribers[project_id] = [q for q in self.subscribers[project_id] if q is not queue]
                if not self.subscribers[project_id]:
                    self.subscribers.pop(project_id, None)
        logger.debug("SSE unsubscribe %s", project_id)

    async def push(self, project_id: str, event: Dict[str, Any]):
        """Push an event to all queues for the project."""
        async with self.lock:
            queues = list(self.subscribers.get(project_id, []))
        if not queues:
            return
        payload = json.dumps(event)
        for queue in queues:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                logger.warning("Queue full for project %s, dropping event", project_id)


broker = RealtimeBroker()
