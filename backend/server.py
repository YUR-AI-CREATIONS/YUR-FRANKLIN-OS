from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Socratic System Prompt - The Ambiguity Detector
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
- NEVER set can_proceed to true if confidence_score < 99.5
- Always find at least 3 ambiguities for any non-trivial request
- Be thorough but not pedantic - focus on architecturally significant decisions
- Questions should be precise and actionable"""

RESOLUTION_SYSTEM_PROMPT = """You are processing user answers to clarification questions for the Sovereign Genesis Platform.

You will receive:
1. The original request
2. Previous ambiguities identified
3. User's answers to those questions

Your task:
1. Incorporate the answers into the specification
2. Check if new ambiguities emerged from the answers
3. Update the confidence score
4. If confidence >= 99.5%, set can_proceed to true

Return JSON in this format:
{
  "resolved_parameters": {
    "parameter_name": "resolved_value"
  },
  "remaining_ambiguities": [...same format as before...],
  "new_ambiguities": [...any new ones discovered...],
  "confidence_score": number,
  "can_proceed": boolean,
  "reasoning": "explanation"
}"""

SPEC_GENERATION_PROMPT = """You are generating a formal specification for the Sovereign Genesis Platform.

You will receive a fully resolved set of requirements. Generate a comprehensive specification document in this format:

{
  "specification": {
    "title": "System Title",
    "version": "1.0.0",
    "generated_at": "ISO timestamp",
    "architecture": {
      "pattern": "e.g., Microservices, Monolith, Event-Driven",
      "components": [
        {
          "name": "Component Name",
          "responsibility": "What it does",
          "interfaces": ["list of interfaces"]
        }
      ]
    },
    "data_model": {
      "entities": [
        {
          "name": "Entity",
          "attributes": [{"name": "attr", "type": "type", "constraints": "any"}]
        }
      ],
      "relationships": ["Entity A -> Entity B: relationship type"]
    },
    "security": {
      "authentication": "method",
      "authorization": "model",
      "encryption": {
        "at_rest": "algorithm",
        "in_transit": "protocol"
      }
    },
    "api_contracts": [
      {
        "endpoint": "/path",
        "method": "HTTP method",
        "request": "schema",
        "response": "schema"
      }
    ],
    "constraints": {
      "performance": "requirements",
      "scalability": "requirements",
      "compliance": ["standards"]
    }
  },
  "verification_checklist": [
    "List of properties that must hold true"
  ]
}"""


# Pydantic Models
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

class GenerateSpecRequest(BaseModel):
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    original_prompt: str
    analysis: Dict[str, Any]
    resolved_parameters: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    confidence_score: float
    can_proceed: bool
    created_at: str
    updated_at: str

class SpecificationResponse(BaseModel):
    session_id: str
    specification: Dict[str, Any]
    generated_at: str


# Helper function to create LLM chat instance
def create_chat(session_id: str, system_message: str) -> LlmChat:
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message
    )
    chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
    return chat


import json
import re

def extract_json_from_response(response: str) -> Dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try to find JSON in code blocks first
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(code_block_pattern, response)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # Try parsing the entire response as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON object pattern
    json_pattern = r'\{[\s\S]*\}'
    match = re.search(json_pattern, response)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    # Return error structure if nothing works
    return {
        "error": "Failed to parse JSON",
        "raw_response": response[:500]
    }


# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Sovereign Genesis Platform - Neural-Symbolic Engine Active"}


@api_router.post("/analyze")
async def analyze_prompt(request: AnalyzeRequest):
    """Analyze a user prompt and identify ambiguities using the Socratic Engine."""
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Create chat instance with Socratic system prompt
        chat = create_chat(f"socratic_{session_id}", SOCRATIC_SYSTEM_PROMPT)
        
        # Send the user's prompt for analysis
        user_message = UserMessage(text=f"Analyze this request: {request.prompt}")
        response = await chat.send_message(user_message)
        
        # Parse the JSON response
        analysis = extract_json_from_response(response)
        
        # Store session in database
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
            "can_proceed": analysis.get("can_proceed", False)
        }
        
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/resolve")
async def resolve_ambiguities(request: ResolveRequest):
    """Process user answers to clarification questions."""
    # Fetch session
    session = await db.sessions.find_one({"session_id": request.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Build context with original prompt and answers
        context = f"""
Original Request: {session['original_prompt']}

Previous Analysis: {json.dumps(session['analysis'], indent=2)}

User Answers:
"""
        for ans in request.answers:
            context += f"- {ans.ambiguity_id}: {ans.answer}"
            if ans.selected_option:
                context += f" (Selected: {ans.selected_option})"
            context += "\n"
        
        # Create chat instance with resolution prompt
        chat = create_chat(f"resolve_{request.session_id}", RESOLUTION_SYSTEM_PROMPT)
        
        user_message = UserMessage(text=context)
        response = await chat.send_message(user_message)
        
        resolution = extract_json_from_response(response)
        
        # Update session
        new_resolved = {**session.get('resolved_parameters', {}), **resolution.get('resolved_parameters', {})}
        
        # Combine remaining and new ambiguities
        all_ambiguities = resolution.get('remaining_ambiguities', []) + resolution.get('new_ambiguities', [])
        
        updated_analysis = {
            **session['analysis'],
            'ambiguities': all_ambiguities,
            'confidence_score': resolution.get('confidence_score', session['analysis'].get('confidence_score', 0)),
            'can_proceed': resolution.get('can_proceed', False)
        }
        
        # Update conversation history
        conversation_history = session.get('conversation_history', [])
        conversation_history.append({"role": "user", "content": request.answers})
        conversation_history.append({"role": "assistant", "content": resolution})
        
        await db.sessions.update_one(
            {"session_id": request.session_id},
            {"$set": {
                "analysis": updated_analysis,
                "resolved_parameters": new_resolved,
                "conversation_history": conversation_history,
                "confidence_score": resolution.get('confidence_score', 0),
                "can_proceed": resolution.get('can_proceed', False),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "session_id": request.session_id,
            "resolution": resolution,
            "resolved_parameters": new_resolved,
            "confidence_score": resolution.get('confidence_score', 0),
            "can_proceed": resolution.get('can_proceed', False)
        }
        
    except Exception as e:
        logging.error(f"Resolution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/generate-spec")
async def generate_specification(request: GenerateSpecRequest):
    """Generate formal specification once all ambiguities are resolved."""
    session = await db.sessions.find_one({"session_id": request.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.get('can_proceed', False):
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot generate spec. Confidence score: {session.get('confidence_score', 0)}%. Must be >= 99.5%"
        )
    
    try:
        # Build complete requirements context
        context = f"""
Original Request: {session['original_prompt']}

Resolved Parameters:
{json.dumps(session.get('resolved_parameters', {}), indent=2)}

Generate a comprehensive formal specification.
"""
        
        chat = create_chat(f"spec_{request.session_id}", SPEC_GENERATION_PROMPT)
        
        user_message = UserMessage(text=context)
        response = await chat.send_message(user_message)
        
        spec = extract_json_from_response(response)
        
        # Store specification
        spec_doc = {
            "session_id": request.session_id,
            "specification": spec,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.specifications.update_one(
            {"session_id": request.session_id},
            {"$set": spec_doc},
            upsert=True
        )
        
        return spec_doc
        
    except Exception as e:
        logging.error(f"Spec generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve a session by ID."""
    session = await db.sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@api_router.get("/sessions")
async def list_sessions(limit: int = 20):
    """List recent sessions."""
    sessions = await db.sessions.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"sessions": sessions}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
