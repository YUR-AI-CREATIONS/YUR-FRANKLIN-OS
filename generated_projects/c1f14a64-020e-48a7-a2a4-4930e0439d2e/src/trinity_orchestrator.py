"""
Trinity Orchestrator - Core system coordination
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@dataclass
class TrinityMessage:
    id: str
    timestamp: str
    sender: str
    receiver: str
    message_type: str
    payload: Dict[str, Any]
    priority: int = 5

class TrinityOrchestrator:
    """Core orchestration system managing all components"""
    
    def __init__(self):
        self.message_queue = asyncio.Queue()
        self.components = {}
        self.running = False
        self.message_handlers = {}
        self.performance_metrics = {
            'messages_processed': 0,
            'errors': 0,
            'uptime': 0,
            'start_time': None
        }
        
    async def initialize(self):
        """Initialize Trinity system"""
        logger.info("🔧 Initializing Trinity Orchestrator...")
        self.performance_metrics['start_time'] = datetime.now()
        self.running = True
        
        # Register default message handlers
        self.register_handler('health_check', self._handle_health_check)
        self.register_handler('system_status', self._handle_system_status)
        self.register_handler('execute_command', self._handle_execute_command)
        
        logger.info("✅ Trinity Orchestrator initialized")
        
    def register_component(self, name: str, component: Any):
        """Register a system component"""
        self.components[name] = component
        logger.info(f"📋 Registered component: {name}")
        
    def register_handler(self, message_type: str, handler):
        """Register message handler"""
        self.message_handlers[message_type] = handler
        
    async def send_message(self, message: TrinityMessage):
        """Send message to the queue"""
        await self.message_queue.put(message)
        
    async def create_message(self, sender: str, receiver: str, 
                           message_type: str, payload: Dict[str, Any],
                           priority: int = 5) -> TrinityMessage:
        """Create and send a new message"""
        message = TrinityMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        await self.send_message(message)
        return message
        
    async def run(self):
        """Main Trinity run loop"""
        logger.info("🔄 Starting Trinity Orchestrator...")
        
        while self.running:
            try:
                # Process messages with timeout
                try:
                    message = await asyncio.wait_for(
                        self.message_queue.get(), timeout=1.0
                    )
                    await self._process_message(message)
                    self.performance_metrics['messages_processed'] += 1
                    
                except asyncio.TimeoutError:
                    # No message received, continue
                    pass
                    
                # Update uptime
                if self.performance_metrics['start_time']:
                    uptime = datetime.now() - self.performance_metrics['start_time']
                    self.performance_metrics['uptime'] = uptime.total_seconds()
                    
            except Exception as e:
                logger.error(f"Trinity error: {e}")
                self.performance_metrics['errors'] += 1
                await asyncio.sleep(1)
                
    async def _process_message(self, message: TrinityMessage):
        """Process incoming message"""
        try:
            logger.debug(f"Processing message: {message.id} - {message.message_type}")
            
            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(message)
            else:
                # Forward to specific component if registered
                if message.receiver in self.components:
                    component = self.components[message.receiver]
                    if hasattr(component, 'handle_message'):
                        await component.handle_message(message)
                else:
                    logger.warning(f"No handler for message type: {message.message_type}")
                    
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            self.performance_metrics['errors'] += 1
            
    async def _handle_health_check(self, message: TrinityMessage):
        """Handle health check requests"""
        response_payload = {
            'status': 'healthy',
            'metrics': self.performance_metrics,
            'components': list(self.components.keys())
        }
        
        response = TrinityMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender='trinity_orchestrator',
            receiver=message.sender,
            message_type='health_response',
            payload=response_payload
        )
        
        await self.send_message(response)
        
    async def _handle_system_status(self, message: TrinityMessage):
        """Handle system status requests"""
        status = {
            'running': self.running,
            'queue_size': self.message_queue.qsize(),
            'components': len(self.components),
            'handlers': len(self.message_handlers),
            'performance': self.performance_metrics
        }
        
        response = await self.create_message(
            sender='trinity_orchestrator',
            receiver=message.sender,
            message_type='status_response',
            payload=status
        )
        
    async def _handle_execute_command(self, message: TrinityMessage):
        """Handle command execution requests"""
        command = message.payload.get('command')
        args = message.payload.get('args', {})
        
        try:
            # Execute command based on type
            if command == 'restart_component':
                await self._restart_component(args.get('component'))
            elif command == 'get_metrics':
                await self._send_metrics(message.sender)
            else:
                logger.warning(f"Unknown command: {command}")
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            
    async def _restart_component(self, component_name: str):
        """Restart a system component"""
        if component_name in self.components:
            component = self.components[component_name]
            if hasattr(component, 'restart'):
                await component.restart()
                logger.info(f"🔄 Restarted component: {component_name}")
            else:
                logger.warning(f"Component {component_name} doesn't support restart")
        else:
            logger.warning(f"Component not found: {component_name}")
            
    async def _send_metrics(self, receiver: str):
        """Send performance metrics"""
        await self.create_message(
            sender='trinity_orchestrator',
            receiver=receiver,
            message_type='metrics_response',
            payload=self.performance_metrics
        )
        
    async def health_check(self) -> bool:
        """Check Trinity health"""
        return self.running and self.performance_metrics['errors'] < 10
        
    async def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'running': self.running,
            'queue_size': self.message_queue.qsize(),
            'components': list(self.components.keys()),
            'performance': self.performance_metrics
        }
        
    async def shutdown(self):
        """Shutdown Trinity system"""
        logger.info("🔄 Shutting down Trinity Orchestrator...")
        self.running = False
        
        # Clear message queue
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
                
        logger.info("✅ Trinity Orchestrator shutdown complete")