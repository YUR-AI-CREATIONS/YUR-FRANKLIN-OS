"""
Socratic Engine API Routes
Handles prompt analysis, ambiguity resolution, and session management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
import uuid
from datetime import datetime, timezone
import json
import re
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient

# Create router
api_router = APIRouter(prefix="/api")

# Global instances (shared with server.py)
# These should be moved to a shared config module later
db = None  # Will be set from server
EMERGENT_LLM_KEY = None

def set_db(database):
    global db
    db = database

def set_emergent_key(key):
    global EMERGENT_LLM_KEY
    EMERGENT_LLM_KEY = key

# ============================================================================
#                        LLM PROVIDER MANAGEMENT
# ============================================================================

from llm_shared import get_llm_provider, initialize_llm_provider

# ============================================================================
#                           SOCRATIC ENGINE PROMPTS
# ============================================================================

SOCRATIC_SYSTEM_PROMPT = """You are the Socratic Pre-Prompt Engine for the Sovereign Genesis Platform. Your role is to analyze user requests for software/system specifications and identify ALL ambiguities before any code generation can proceed.

CRITICAL: You NEVER answer a request directly. You ALWAYS parse it for missing variables and return clarifying questions.

Your analysis protocol:
1. Parse the input into semantic components (entities, actions, constraints)
2. Identify missing parameters across these dimensions:
   - Authentication/Authorization protocols
   - Data persistence (database type, consistency model)
   - Scalability requirements (users, transactions/sec)
   - Security posture (encryption, compliance standards)
   - Integration points (external APIs, services)
   - Error handling and recovery strategies
   - Performance constraints (latency, throughput)
   - User interface requirements (if applicable)

3. Calculate a Specification Confidence Score (0-100%)
4. Return ONLY a JSON response in this exact format:

{
  "input_analysis": {
    "detected_entities": ["list of entities mentioned"],
    "detected_actions": ["list of actions/operations"],
    "detected_constraints": ["list of constraints mentioned"]
  },
  "ambiguities": [
    {
      "id": "AMB_001",
      "category": "one of: AUTH|DATA|SCALE|SECURITY|INTEGRATION|ERROR|PERFORMANCE|UI",
      "description": "What is ambiguous",
      "question": "The clarifying question to ask",
      "options": ["Option A", "Option B", "Option C"],
      "priority": "CRITICAL|HIGH|MEDIUM|LOW"
    }
  ],
  "confidence_score": 0,
  "can_proceed": false,
  "reasoning": "Brief explanation of why specification is incomplete"
}

Rules:
- Set can_proceed to true when confidence_score >= 50 AND no CRITICAL ambiguities remain
- Always find at least 2-3 ambiguities for any non-trivial request
- Be thorough but not pedantic - focus on architecturally significant decisions
- Questions should be precise and actionable"""

# ============================================================================
#                              PYDANTIC MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class ResolutionAnswer(BaseModel):
    ambiguity_id: str
    answer: str
    selected_option: Optional[str] = None

class ResolveRequest(BaseModel):
    session_id: str
    answers: List[ResolutionAnswer]

# ============================================================================
#                              HELPER FUNCTIONS
# ============================================================================

def extract_json_from_response(response: str) -> Dict[str, Any]:
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(code_block_pattern, response)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    json_pattern = r'\{[\s\S]*\}'
    match = re.search(json_pattern, response)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    return {"error": "Failed to parse JSON", "raw_response": response[:500]}

async def generate_with_hybrid_llm(system_prompt: str, user_message: str, 
                                   prefer_local: bool = True) -> Dict[str, Any]:
    """
    Generate response using the hybrid LLM provider.
    Supports automatic switching between cloud and local LLMs.
    
    Returns:
        Dict with 'response', 'provider', 'model', and metadata
    """
    provider = await get_llm_provider()
    result = await provider.generate(
        system_prompt=system_prompt,
        user_message=user_message,
        prefer_local=prefer_local,
        temperature=0.7
    )
    return result

# ============================================================================
#                           CORE API ENDPOINTS
# ============================================================================

@api_router.get("/")
async def root():
    return {
        "message": "Sovereign Genesis Platform - Neural-Symbolic Engine Active",
        "version": "2.0.0",
        "modules": ["Socratic Engine", "Genesis Kernel", "Ouroboros Loop", 
                    "Quality Gate", "Governance Engine", "Multi-Kernel Orchestrator"]
    }

@api_router.post("/analyze")
async def analyze_prompt(request: AnalyzeRequest):
    """Analyze a user prompt using the Socratic Engine with hybrid LLM support"""
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Use hybrid LLM provider (respects cloud/local mode setting)
        result = await generate_with_hybrid_llm(
            system_prompt=SOCRATIC_SYSTEM_PROMPT,
            user_message=f"Analyze this request: {request.prompt}",
            prefer_local=True  # Default to local for cost savings
        )
        
        analysis = extract_json_from_response(result["response"])
        
        session_doc = {
            "session_id": session_id,
            "original_prompt": request.prompt,
            "analysis": analysis,
            "resolved_parameters": {},
            "conversation_history": [
                {"role": "user", "content": request.prompt},
                {"role": "assistant", "content": analysis}
            ],
            "confidence_score": analysis.get("confidence_score", 0),
            "can_proceed": analysis.get("can_proceed", False),
            "llm_provider": result.get("provider", "unknown"),
            "llm_model": result.get("model", "unknown"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": session_doc},
            upsert=True
        )
        
        return {
            "session_id": session_id,
            "analysis": analysis,
            "confidence_score": analysis.get("confidence_score", 0),
            "can_proceed": analysis.get("can_proceed", False),
            "llm_info": {
                "provider": result.get("provider"),
                "model": result.get("model")
            }
        }
        
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/resolve")
async def resolve_ambiguities(request: ResolveRequest):
    """Process user answers to clarification questions using hybrid LLM"""
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    session = await db.sessions.find_one({"session_id": request.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update resolved parameters
    resolved_params = session.get("resolved_parameters", {})
    for answer in request.answers:
        resolved_params[answer.ambiguity_id] = {
            "answer": answer.answer,
            "selected_option": answer.selected_option
        }
    
    # Generate refined specification
    context = f"""
Original prompt: {session['original_prompt']}
Analysis: {json.dumps(session['analysis'], indent=2)}
Resolved parameters: {json.dumps(resolved_params, indent=2)}

Generate a complete specification document that addresses all ambiguities.
"""
    
    try:
        result = await generate_with_hybrid_llm(
            system_prompt="You are a specification generator. Create a complete, unambiguous specification document.",
            user_message=context,
            prefer_local=True
        )
        
        specification = extract_json_from_response(result["response"])
        
        # Update session
        await db.sessions.update_one(
            {"session_id": request.session_id},
            {"$set": {
                "resolved_parameters": resolved_params,
                "specification": specification,
                "confidence_score": 100,
                "can_proceed": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "session_id": request.session_id,
            "specification": specification,
            "confidence_score": 100,
            "can_proceed": True
        }
        
    except Exception as e:
        logging.error(f"Resolution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    session = await db.sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@api_router.get("/sessions")
async def list_sessions(limit: int = 10):
    """List recent sessions"""
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    sessions = await db.sessions.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=limit)
    return {"sessions": sessions}