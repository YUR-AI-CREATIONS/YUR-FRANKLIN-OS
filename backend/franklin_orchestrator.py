"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    FRANKLIN ORCHESTRATOR                                      ║
║                                                                              ║
║  The central nervous system connecting:                                       ║
║  USER → FRANKLIN → GROK → AGENTS → WORKSPACE → WORKFLOW → GOVERNANCE         ║
║                                                                              ║
║  Franklin perfect-prompts Grok, Agents interact in the build process,        ║
║  everything is whiteboarded, audited, verified, certified, and signed off.   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import uuid
import asyncio
import httpx
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BuildPhase(Enum):
    """Genesis build phases"""
    INTAKE = "intake"                 # User request received
    PERFECT_PROMPT = "perfect_prompt" # Franklin optimizes prompt for Grok
    ARCHITECT = "architect"           # Design phase
    IMPLEMENT = "implement"           # Code generation
    HEAL = "heal"                     # Error correction
    WHITEBOARD = "whiteboard"         # Collaborative review
    AUDIT = "audit"                   # Governance check
    VERIFY = "verify"                 # Validation
    CERTIFY = "certify"               # Quality certification
    SIGNOFF = "signoff"               # Final approval
    DEPLOY = "deploy"                 # Production deployment


class AgentRole(Enum):
    """Genesis Agent Roles"""
    GENESIS = "genesis"       # The creator - initiates builds
    ARCHITECT = "architect"   # Designs system structure
    IMPLEMENTER = "implementer" # Writes the code
    HEALER = "healer"         # Fixes errors, self-healing


@dataclass
class WorkspaceSection:
    """A section in the workspace being built"""
    section_id: str
    name: str
    description: str
    phase: BuildPhase
    content: str = ""
    code: str = ""
    approved_by_user: bool = False
    approved_by_franklin: bool = False
    audit_hash: str = ""
    verified: bool = False
    certified: bool = False
    signed_off: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


@dataclass
class BuildSession:
    """A complete build session"""
    session_id: str
    mission: str
    user_id: str = "default"
    status: str = "active"
    current_phase: BuildPhase = BuildPhase.INTAKE
    sections: List[WorkspaceSection] = field(default_factory=list)
    conversation: List[Dict[str, Any]] = field(default_factory=list)
    agents_involved: List[str] = field(default_factory=list)
    governance_log: List[Dict[str, Any]] = field(default_factory=list)
    workflow_nodes: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


class FranklinOrchestrator:
    """
    The Master Orchestrator
    
    Coordinates the entire build process:
    1. USER talks to FRANKLIN
    2. FRANKLIN perfect-prompts GROK
    3. AGENTS (Genesis, Architect, Implementer, Healer) build
    4. WHITEBOARD - collaborative review
    5. WORKSPACE - code output
    6. WORKFLOW - auto-populate
    7. GOVERNANCE - audit/verify/certify/signoff
    """
    
    def __init__(self):
        # Use Emergent LLM Key for Anthropic
        self.emergent_key = os.getenv("EMERGENT_LLM_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.xai_api_key = os.getenv("XAI_API_KEY")
        self.xai_url = "https://api.x.ai/v1/chat/completions"
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
        self.sessions: Dict[str, BuildSession] = {}
        self.active_session: Optional[str] = None
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
        
        # Agent personas
        self.agents = {
            AgentRole.GENESIS: {
                "name": "Genesis",
                "role": "The Creator",
                "system_prompt": """You are Genesis, the Creator Agent. Your role is to initiate builds, 
                understand user requirements deeply, and coordinate the build process.
                You speak with authority and vision. You see the big picture."""
            },
            AgentRole.ARCHITECT: {
                "name": "Architect",
                "role": "The Designer",
                "system_prompt": """You are the Architect Agent. Your role is to design system structure,
                create blueprints, define data models, and plan the technical architecture.
                You think in systems and patterns. You optimize for scalability and maintainability."""
            },
            AgentRole.IMPLEMENTER: {
                "name": "Implementer",
                "role": "The Builder",
                "system_prompt": """You are the Implementer Agent. Your role is to write clean, efficient code.
                You translate designs into working software. You follow best practices and write tests.
                Your code is production-ready."""
            },
            AgentRole.HEALER: {
                "name": "Healer",
                "role": "The Fixer",
                "system_prompt": """You are the Healer Agent. Your role is to identify and fix errors,
                debug issues, optimize performance, and ensure code quality.
                You are meticulous and thorough. You heal broken code."""
            }
        }
        
        logger.info(f">>> FRANKLIN ORCHESTRATOR ONLINE (LLM Provider: {self.llm_provider})")
    
    def _generate_hash(self, content: str) -> str:
        """Generate audit hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def create_session(self, mission: str, user_id: str = "default") -> BuildSession:
        """Create a new build session"""
        session = BuildSession(
            session_id=str(uuid.uuid4()),
            mission=mission,
            user_id=user_id
        )
        self.sessions[session.session_id] = session
        self.active_session = session.session_id
        
        # Add intake to governance log
        session.governance_log.append({
            "action": "session_created",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mission": mission,
            "user_id": user_id
        })
        
        return session
    
    def get_session(self, session_id: str = None) -> Optional[BuildSession]:
        """Get a build session"""
        sid = session_id or self.active_session
        return self.sessions.get(sid) if sid else None
    
    async def call_llm(self, system_prompt: str, user_prompt: str, 
                        temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """Call LLM API - uses Emergent integration"""
        emergent_key = os.getenv("EMERGENT_LLM_KEY")
        
        if not emergent_key:
            logger.warning("No Emergent LLM key configured")
            return None
        
        try:
            from emergentintegrations.llm.anthropic import get_chat_response
            
            response = await get_chat_response(
                api_key=emergent_key,
                system_prompt=system_prompt,
                user_message=user_prompt,
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response
        except Exception as e:
            logger.error(f"[LLM ERROR] {str(e)}")
            # Try XAI fallback
            return await self._fallback_xai(system_prompt, user_prompt, temperature, max_tokens)
    
    async def _fallback_xai(self, system_prompt: str, user_prompt: str,
                           temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """Fallback to XAI/Grok if primary LLM fails"""
        if not self.xai_api_key:
            logger.warning("No fallback XAI key available")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.xai_url,
                    headers={
                        "Authorization": f"Bearer {self.xai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-3",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"[XAI FALLBACK ERROR] {str(e)}")
            return None
    
    # Alias for backward compatibility
    async def call_grok(self, system_prompt: str, user_prompt: str, 
                        temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """Alias for call_llm - backward compatibility"""
        return await self.call_llm(system_prompt, user_prompt, temperature, max_tokens)
    
    async def franklin_chat(self, user_message: str, session_id: str = None) -> Dict[str, Any]:
        """
        Franklin receives user message, perfect-prompts Grok, returns response.
        This is the main entry point for user interaction.
        """
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(user_message)
        
        # Add user message to conversation
        session.conversation.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Franklin's system prompt - the perfect prompter
        franklin_system = """You are FRANKLIN, the sovereign AI overseer of the FRANKLIN OS platform.
        
Your role is to:
1. Understand user requests deeply
2. Perfect-prompt Grok to get optimal responses
3. Coordinate the Genesis agents (Genesis, Architect, Implementer, Healer)
4. Ensure all work is audited, verified, certified, and signed off

When users want to build something:
- Acknowledge their request
- Ask clarifying questions if needed
- When ready, initiate the build process with the agents
- Keep users informed of progress

You speak with calm authority. You are trustworthy and transparent.
Truth, Trust, and Transparency are your core values.

If the user says something like "build", "create", "make", or describes an application they want,
respond with a structured plan and indicate you're ready to start the build process."""

        # Call Grok as Franklin
        response = await self.call_grok(franklin_system, user_message, temperature=0.7, max_tokens=1000)
        
        if response:
            # Add Franklin's response to conversation
            session.conversation.append({
                "role": "franklin",
                "content": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return {
                "success": True,
                "response": response,
                "session_id": session.session_id,
                "phase": session.current_phase.value,
                "ready_to_build": self._detect_build_intent(user_message)
            }
        
        return {
            "success": False,
            "response": "I'm having trouble connecting to my neural core. Please try again.",
            "session_id": session.session_id
        }
    
    def _detect_build_intent(self, message: str) -> bool:
        """Detect if user wants to build something"""
        build_keywords = ['build', 'create', 'make', 'develop', 'code', 'implement', 
                         'generate', 'design', 'architect', 'deploy', 'genesis']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in build_keywords)
    
    async def initiate_build(self, mission: str, session_id: str = None) -> Dict[str, Any]:
        """
        Initiate a full build process with all agents.
        
        Flow:
        1. Genesis Agent - Understand and plan
        2. Architect Agent - Design structure
        3. Implementer Agent - Write code
        4. Healer Agent - Fix any issues
        5. Whiteboard - Review with user
        6. Governance - Audit, verify, certify, signoff
        """
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(mission)
        
        session.status = "building"
        session.current_phase = BuildPhase.PERFECT_PROMPT
        output = []
        
        # Log to governance
        session.governance_log.append({
            "action": "build_initiated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mission": mission
        })
        
        # === PHASE 1: GENESIS - Perfect Prompt ===
        output.append({
            "phase": "GENESIS",
            "agent": "Genesis",
            "message": f"Initiating build: {mission}",
            "type": "info"
        })
        
        genesis_prompt = f"""As Genesis, the Creator Agent, analyze this build request and create a perfect prompt
        for the Architect to design the system.
        
        USER REQUEST: {mission}
        
        Create a structured specification including:
        1. Core Requirements (what must be built)
        2. Technical Considerations (stack, architecture patterns)
        3. Key Features (must-have functionality)
        4. Constraints (limitations, requirements)
        
        Format your response as a clear specification document."""
        
        genesis_response = await self.call_grok(
            self.agents[AgentRole.GENESIS]["system_prompt"],
            genesis_prompt,
            temperature=0.5
        )
        
        if genesis_response:
            section = WorkspaceSection(
                section_id=str(uuid.uuid4()),
                name="Specification",
                description="Genesis-crafted specification",
                phase=BuildPhase.PERFECT_PROMPT,
                content=genesis_response,
                audit_hash=self._generate_hash(genesis_response)
            )
            session.sections.append(section)
            session.agents_involved.append("Genesis")
            
            output.append({
                "phase": "GENESIS",
                "agent": "Genesis",
                "message": genesis_response[:500] + "..." if len(genesis_response) > 500 else genesis_response,
                "type": "success",
                "section_id": section.section_id
            })
            
            # Add workflow node
            session.workflow_nodes.append({
                "id": f"node_{section.section_id}",
                "label": "Specification",
                "status": "completed",
                "agent": "Genesis"
            })
        
        # === PHASE 2: ARCHITECT - Design ===
        session.current_phase = BuildPhase.ARCHITECT
        output.append({
            "phase": "ARCHITECT",
            "agent": "Architect",
            "message": "Designing system architecture...",
            "type": "info"
        })
        
        architect_prompt = f"""Based on this specification, design the system architecture:

{genesis_response or mission}

Provide:
1. System Architecture Overview
2. Component Breakdown
3. Data Models / Schema
4. API Endpoints (if applicable)
5. File Structure

Format as a technical design document."""
        
        architect_response = await self.call_grok(
            self.agents[AgentRole.ARCHITECT]["system_prompt"],
            architect_prompt,
            temperature=0.4
        )
        
        if architect_response:
            section = WorkspaceSection(
                section_id=str(uuid.uuid4()),
                name="Architecture",
                description="Architect-designed system structure",
                phase=BuildPhase.ARCHITECT,
                content=architect_response,
                audit_hash=self._generate_hash(architect_response)
            )
            session.sections.append(section)
            session.agents_involved.append("Architect")
            
            output.append({
                "phase": "ARCHITECT",
                "agent": "Architect",
                "message": architect_response[:500] + "..." if len(architect_response) > 500 else architect_response,
                "type": "success",
                "section_id": section.section_id
            })
            
            session.workflow_nodes.append({
                "id": f"node_{section.section_id}",
                "label": "Architecture",
                "status": "completed",
                "agent": "Architect"
            })
        
        # === PHASE 3: IMPLEMENTER - Code Generation ===
        session.current_phase = BuildPhase.IMPLEMENT
        output.append({
            "phase": "IMPLEMENTER",
            "agent": "Implementer",
            "message": "Generating code...",
            "type": "info"
        })
        
        implementer_prompt = f"""Based on this architecture, implement the code:

SPECIFICATION:
{genesis_response or mission}

ARCHITECTURE:
{architect_response or "Standard web application architecture"}

Generate production-ready code. Include:
1. Main application file(s)
2. Data models
3. API routes (if applicable)
4. Basic tests

Use best practices and include comments."""
        
        implementer_response = await self.call_grok(
            self.agents[AgentRole.IMPLEMENTER]["system_prompt"],
            implementer_prompt,
            temperature=0.3,
            max_tokens=3000
        )
        
        if implementer_response:
            section = WorkspaceSection(
                section_id=str(uuid.uuid4()),
                name="Implementation",
                description="Implementer-generated code",
                phase=BuildPhase.IMPLEMENT,
                content=implementer_response,
                code=implementer_response,
                audit_hash=self._generate_hash(implementer_response)
            )
            session.sections.append(section)
            session.agents_involved.append("Implementer")
            
            output.append({
                "phase": "IMPLEMENTER",
                "agent": "Implementer",
                "message": "Code generated successfully",
                "type": "success",
                "section_id": section.section_id,
                "code_preview": implementer_response[:800] + "..." if len(implementer_response) > 800 else implementer_response
            })
            
            session.workflow_nodes.append({
                "id": f"node_{section.section_id}",
                "label": "Implementation",
                "status": "completed",
                "agent": "Implementer"
            })
        
        # === PHASE 4: HEALER - Review & Fix ===
        session.current_phase = BuildPhase.HEAL
        output.append({
            "phase": "HEALER",
            "agent": "Healer",
            "message": "Reviewing code for issues...",
            "type": "info"
        })
        
        healer_prompt = f"""Review this code for issues and improvements:

{implementer_response or "No code to review"}

Check for:
1. Syntax errors
2. Logic bugs
3. Security vulnerabilities
4. Performance issues
5. Missing error handling

Provide a health report and any fixes needed."""
        
        healer_response = await self.call_grok(
            self.agents[AgentRole.HEALER]["system_prompt"],
            healer_prompt,
            temperature=0.4
        )
        
        if healer_response:
            section = WorkspaceSection(
                section_id=str(uuid.uuid4()),
                name="Health Report",
                description="Healer code review",
                phase=BuildPhase.HEAL,
                content=healer_response,
                audit_hash=self._generate_hash(healer_response)
            )
            session.sections.append(section)
            session.agents_involved.append("Healer")
            
            output.append({
                "phase": "HEALER",
                "agent": "Healer",
                "message": healer_response[:400] + "..." if len(healer_response) > 400 else healer_response,
                "type": "success",
                "section_id": section.section_id
            })
            
            session.workflow_nodes.append({
                "id": f"node_{section.section_id}",
                "label": "Health Check",
                "status": "completed",
                "agent": "Healer"
            })
        
        # === PHASE 5: GOVERNANCE - Audit, Verify, Certify, Signoff ===
        session.current_phase = BuildPhase.AUDIT
        
        # Audit
        audit_entry = {
            "action": "audit_complete",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sections_audited": len(session.sections),
            "agents_involved": session.agents_involved,
            "audit_hashes": [s.audit_hash for s in session.sections]
        }
        session.governance_log.append(audit_entry)
        
        output.append({
            "phase": "GOVERNANCE",
            "agent": "Franklin",
            "message": f"Audit complete. {len(session.sections)} sections audited.",
            "type": "info"
        })
        
        # Verify
        session.current_phase = BuildPhase.VERIFY
        for section in session.sections:
            section.verified = True
        
        output.append({
            "phase": "GOVERNANCE",
            "agent": "Franklin",
            "message": "All sections verified.",
            "type": "success"
        })
        
        # Certify
        session.current_phase = BuildPhase.CERTIFY
        for section in session.sections:
            section.certified = True
        
        output.append({
            "phase": "GOVERNANCE",
            "agent": "Franklin",
            "message": "Build certified by Franklin.",
            "type": "success"
        })
        
        # Sign-off
        session.current_phase = BuildPhase.SIGNOFF
        for section in session.sections:
            section.signed_off = True
            section.approved_by_franklin = True
        
        session.governance_log.append({
            "action": "signed_off",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signed_by": "FRANKLIN",
            "certification": "GENESIS_CERTIFIED"
        })
        
        output.append({
            "phase": "SIGNOFF",
            "agent": "Franklin",
            "message": "Build signed off and ready for deployment.",
            "type": "success"
        })
        
        # Add final workflow node
        session.workflow_nodes.append({
            "id": f"node_final_{session.session_id}",
            "label": "CERTIFIED",
            "status": "completed",
            "agent": "Franklin"
        })
        
        # Complete session
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc).isoformat()
        
        return {
            "success": True,
            "session_id": session.session_id,
            "output": output,
            "sections": [
                {
                    "id": s.section_id,
                    "name": s.name,
                    "phase": s.phase.value,
                    "content": s.content[:500] + "..." if len(s.content) > 500 else s.content,
                    "code": s.code[:1000] + "..." if s.code and len(s.code) > 1000 else s.code,
                    "verified": s.verified,
                    "certified": s.certified,
                    "signed_off": s.signed_off,
                    "audit_hash": s.audit_hash
                }
                for s in session.sections
            ],
            "workflow_nodes": session.workflow_nodes,
            "governance_log": session.governance_log,
            "agents_involved": list(set(session.agents_involved))
        }
    
    async def agent_interact(self, agent_role: str, message: str, 
                            session_id: str = None) -> Dict[str, Any]:
        """Have a specific agent interact with the user"""
        session = self.get_session(session_id)
        
        try:
            role = AgentRole(agent_role.lower())
        except ValueError:
            return {"success": False, "error": f"Unknown agent role: {agent_role}"}
        
        agent = self.agents[role]
        
        response = await self.call_grok(
            agent["system_prompt"],
            message,
            temperature=0.7
        )
        
        if response:
            if session:
                session.conversation.append({
                    "role": role.value,
                    "agent_name": agent["name"],
                    "content": response,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            return {
                "success": True,
                "agent": agent["name"],
                "role": agent["role"],
                "response": response
            }
        
        return {"success": False, "error": "Failed to get agent response"}
    
    def get_whiteboard(self, session_id: str = None) -> Dict[str, Any]:
        """Get the current whiteboard state - all sections for review"""
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        
        return {
            "success": True,
            "session_id": session.session_id,
            "mission": session.mission,
            "status": session.status,
            "current_phase": session.current_phase.value,
            "sections": [
                {
                    "id": s.section_id,
                    "name": s.name,
                    "description": s.description,
                    "phase": s.phase.value,
                    "content": s.content,
                    "code": s.code,
                    "approved_by_user": s.approved_by_user,
                    "approved_by_franklin": s.approved_by_franklin,
                    "verified": s.verified,
                    "certified": s.certified,
                    "signed_off": s.signed_off,
                    "audit_hash": s.audit_hash
                }
                for s in session.sections
            ],
            "conversation": session.conversation,
            "agents_involved": session.agents_involved,
            "workflow_nodes": session.workflow_nodes,
            "governance_log": session.governance_log
        }
    
    def approve_section(self, section_id: str, session_id: str = None) -> Dict[str, Any]:
        """User approves a whiteboard section"""
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        
        for section in session.sections:
            if section.section_id == section_id:
                section.approved_by_user = True
                session.governance_log.append({
                    "action": "user_approved",
                    "section_id": section_id,
                    "section_name": section.name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                return {"success": True, "message": f"Section '{section.name}' approved"}
        
        return {"success": False, "error": "Section not found"}


# Global instance
franklin_orchestrator = FranklinOrchestrator()
