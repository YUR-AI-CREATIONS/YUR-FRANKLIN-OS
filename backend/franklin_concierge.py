"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       FRANKLIN CONCIERGE ENGINE                              ║
║                                                                              ║
║  The intelligent intake layer. Franklin's job is NEVER to lose the user.    ║
║                                                                              ║
║  Modes:                                                                      ║
║    SILENT   — "just build it" — zero friction, best-guess spec, auto-start ║
║    BALANCED — default — ask only critical questions, confirm contract        ║
║    VERBOSE  — "show me everything" — every decision surfaced for approval    ║
║                                                                              ║
║  Flow:                                                                       ║
║    Raw Input → Classify → Ambiguity Score → [Questions?] → Build Contract   ║
║             → Confirm → Genesis Pipeline → Cert → Deploy                    ║
║                                                                              ║
║  Competitor targets: Cursor, Devin, Emergent, Supercool                     ║
║  Differentiator: transparency, user control, no BS, real deployment         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import uuid
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# ENUMS & CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

class UserMode(Enum):
    SILENT   = "silent"    # Build now, ask nothing
    BALANCED = "balanced"  # Ask only critical gaps
    VERBOSE  = "verbose"   # Surface every decision


class ProjectType(Enum):
    WEB_APP       = "web_app"
    API_SERVICE   = "api_service"
    MOBILE_APP    = "mobile_app"
    CLI_TOOL      = "cli_tool"
    DATA_PIPELINE = "data_pipeline"
    AI_AGENT      = "ai_agent"
    ECOMMERCE     = "ecommerce"
    SAAS_PLATFORM = "saas_platform"
    LANDING_PAGE  = "landing_page"
    UNKNOWN       = "unknown"


class SessionState(Enum):
    INTAKE       = "intake"       # Receiving initial input
    CLARIFYING   = "clarifying"   # Asking questions
    CONFIRMING   = "confirming"   # Showing build contract for approval
    BUILDING     = "building"     # Genesis pipeline running
    CERTIFYING   = "certifying"   # 8-gate certification
    DEPLOYING    = "deploying"    # Pushing to production
    COMPLETE     = "complete"     # Done, delivered
    FAILED       = "failed"       # Build failed — never acceptable, triggers heal


SILENT_TRIGGERS = {
    "just build", "build it", "go", "just do it", "no questions",
    "skip questions", "auto", "straight build", "silent mode", "just ship"
}

VERBOSE_TRIGGERS = {
    "show me everything", "verbose", "step by step", "explain everything",
    "granular", "every decision", "i want to see", "walk me through"
}

# Project type keyword mapping
PROJECT_KEYWORDS: Dict[ProjectType, List[str]] = {
    ProjectType.WEB_APP:       ["web app", "website", "web application", "dashboard", "portal", "frontend"],
    ProjectType.API_SERVICE:   ["api", "rest", "graphql", "backend", "service", "microservice", "endpoint"],
    ProjectType.MOBILE_APP:    ["mobile", "ios", "android", "react native", "flutter", "app"],
    ProjectType.CLI_TOOL:      ["cli", "command line", "terminal", "script", "tool"],
    ProjectType.DATA_PIPELINE: ["data pipeline", "etl", "analytics", "bigquery", "airflow", "spark"],
    ProjectType.AI_AGENT:      ["ai agent", "llm", "chatbot", "gpt", "assistant", "rag", "embedding"],
    ProjectType.ECOMMERCE:     ["ecommerce", "shop", "store", "checkout", "products", "cart", "stripe"],
    ProjectType.SAAS_PLATFORM: ["saas", "platform", "subscription", "multi-tenant", "b2b", "enterprise"],
    ProjectType.LANDING_PAGE:  ["landing page", "marketing site", "homepage", "waitlist"],
}

# Tech stack defaults by project type
TECH_DEFAULTS: Dict[ProjectType, Dict] = {
    ProjectType.WEB_APP:       {"frontend": "React 19", "backend": "FastAPI", "db": "PostgreSQL", "deploy": "Render"},
    ProjectType.API_SERVICE:   {"frontend": None, "backend": "FastAPI", "db": "PostgreSQL", "deploy": "Render"},
    ProjectType.MOBILE_APP:    {"frontend": "React Native", "backend": "FastAPI", "db": "Supabase", "deploy": "Expo"},
    ProjectType.CLI_TOOL:      {"frontend": None, "backend": "Python", "db": None, "deploy": "PyPI"},
    ProjectType.DATA_PIPELINE: {"frontend": None, "backend": "Python/Airflow", "db": "BigQuery", "deploy": "GCP"},
    ProjectType.AI_AGENT:      {"frontend": "React 19", "backend": "FastAPI", "db": "Supabase+pgvector", "deploy": "Render"},
    ProjectType.ECOMMERCE:     {"frontend": "React 19", "backend": "FastAPI", "db": "PostgreSQL", "deploy": "Render"},
    ProjectType.SAAS_PLATFORM: {"frontend": "React 19", "backend": "FastAPI", "db": "Supabase", "deploy": "Render"},
    ProjectType.LANDING_PAGE:  {"frontend": "Next.js", "backend": None, "db": None, "deploy": "Vercel"},
    ProjectType.UNKNOWN:       {"frontend": "React 19", "backend": "FastAPI", "db": "PostgreSQL", "deploy": "Render"},
}


# ──────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ClarifyingQuestion:
    question_id: str
    question: str
    purpose: str           # Why this question matters
    options: List[str]     # Suggested answers (user can type custom)
    required: bool = True
    answered: bool = False
    answer: str = ""


@dataclass
class BuildContract:
    """The locked specification. Nothing builds without a signed contract."""
    contract_id: str
    session_id: str
    project_name: str
    project_type: ProjectType
    mission: str                    # One-sentence mission statement
    full_description: str           # Full elaborated description
    user_mode: UserMode
    tech_stack: Dict[str, str]
    features: List[str]             # Confirmed feature list
    auth_required: bool
    database_needed: bool
    deployment_target: str
    timeline_estimate: str          # "Simple: ~2min" / "Complex: ~8min"
    questions_asked: List[Dict]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confirmed_at: Optional[str] = None
    contract_hash: str = ""

    def sign(self) -> str:
        """Generate the cryptographic contract hash."""
        payload = json.dumps({
            "contract_id": self.contract_id,
            "mission": self.mission,
            "features": self.features,
            "tech_stack": self.tech_stack,
            "created_at": self.created_at,
        }, sort_keys=True)
        self.contract_hash = hashlib.sha256(payload.encode()).hexdigest()
        self.confirmed_at = datetime.now(timezone.utc).isoformat()
        return self.contract_hash


@dataclass
class ConciergeSession:
    session_id: str
    raw_input: str
    user_mode: UserMode
    state: SessionState
    project_type: ProjectType
    ambiguity_score: float          # 0.0 = crystal clear, 10.0 = total chaos
    questions: List[ClarifyingQuestion]
    current_question_idx: int
    build_contract: Optional[BuildContract]
    conversation: List[Dict]        # Full conversation history
    build_id: Optional[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ──────────────────────────────────────────────────────────────────────────────
# CONCIERGE ENGINE
# ──────────────────────────────────────────────────────────────────────────────

class FranklinConcierge:
    """
    Franklin's intake and orchestration layer.

    This is the UX brain. Its job:
    1. Never lose the user
    2. Never start a build without sufficient clarity
    3. Never leave a build unfinished
    4. Every build = real working code + deployed + certified
    """

    def __init__(self, llm_caller=None):
        """
        Args:
            llm_caller: async callable(system_prompt, user_prompt) -> str
                        Inject the FranklinOrchestrator.call_llm method
        """
        self.llm = llm_caller
        self.sessions: Dict[str, ConciergeSession] = {}

    # ──────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────────────────────────────────

    async def intake(self, raw_input: str, user_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Entry point. Accepts raw user input (vague or precise).
        Returns either:
          - A question to ask the user, OR
          - A build contract ready for confirmation, OR
          - An immediate build start (silent mode)
        """
        session_id = str(uuid.uuid4())

        # Detect user mode from input if not explicitly set
        detected_mode = self._detect_mode(raw_input, user_mode)

        # Classify the project
        project_type = self._classify_project(raw_input)

        # Score ambiguity
        ambiguity = self._score_ambiguity(raw_input, project_type)

        # Generate clarifying questions (if needed)
        questions = await self._generate_questions(raw_input, project_type, ambiguity, detected_mode)

        session = ConciergeSession(
            session_id=session_id,
            raw_input=raw_input,
            user_mode=detected_mode,
            state=SessionState.INTAKE,
            project_type=project_type,
            ambiguity_score=ambiguity,
            questions=questions,
            current_question_idx=0,
            build_contract=None,
            conversation=[{"role": "user", "content": raw_input, "ts": datetime.now(timezone.utc).isoformat()}],
            build_id=None,
        )
        self.sessions[session_id] = session

        logger.info(f"Intake: session={session_id}, type={project_type.value}, ambiguity={ambiguity:.1f}, mode={detected_mode.value}")

        # Route based on mode and ambiguity
        if detected_mode == UserMode.SILENT or (ambiguity < 2.5 and detected_mode != UserMode.VERBOSE):
            # Clear enough — go straight to contract
            contract = await self._generate_contract(session)
            session.build_contract = contract
            session.state = SessionState.CONFIRMING
            return self._response_contract_ready(session)

        elif questions:
            session.state = SessionState.CLARIFYING
            return self._response_ask_question(session)

        else:
            contract = await self._generate_contract(session)
            session.build_contract = contract
            session.state = SessionState.CONFIRMING
            return self._response_contract_ready(session)

    async def respond(self, session_id: str, user_response: str) -> Dict[str, Any]:
        """
        Handle user's answer to a clarifying question.
        Advances the conversation until contract is ready.
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found", "session_id": session_id}

        session.updated_at = datetime.now(timezone.utc).isoformat()
        session.conversation.append({
            "role": "user",
            "content": user_response,
            "ts": datetime.now(timezone.utc).isoformat()
        })

        if session.state == SessionState.CLARIFYING:
            # Record the answer
            q = session.questions[session.current_question_idx]
            q.answer = user_response
            q.answered = True
            session.current_question_idx += 1

            # More questions?
            remaining = [q for q in session.questions if not q.answered]
            if remaining and session.user_mode != UserMode.SILENT:
                return self._response_ask_question(session)
            else:
                # All questions answered — generate contract
                contract = await self._generate_contract(session)
                session.build_contract = contract
                session.state = SessionState.CONFIRMING
                return self._response_contract_ready(session)

        elif session.state == SessionState.CONFIRMING:
            # User is responding to the contract confirmation
            confirmed = self._parse_confirmation(user_response)
            if confirmed:
                session.build_contract.sign()
                session.state = SessionState.BUILDING
                return {
                    "action": "build_start",
                    "session_id": session_id,
                    "contract_id": session.build_contract.contract_id,
                    "contract_hash": session.build_contract.contract_hash,
                    "message": f"Contract signed. Building {session.build_contract.project_name}. {session.build_contract.timeline_estimate}",
                    "contract": self._serialize_contract(session.build_contract),
                    "stream_url": f"/api/concierge/{session_id}/stream",
                }
            else:
                # User wants changes — go back to clarifying
                session.state = SessionState.CLARIFYING
                # Reset questions and ask what to change
                change_question = ClarifyingQuestion(
                    question_id="revision",
                    question="What would you like to change about the plan?",
                    purpose="Refine the build contract before starting",
                    options=["Change the tech stack", "Add more features", "Simplify scope", "Change the deployment target"],
                    required=True,
                )
                session.questions = [change_question]
                session.current_question_idx = 0
                return self._response_ask_question(session)

        return {"error": "Unexpected session state", "state": session.state.value}

    async def confirm(self, session_id: str) -> Dict[str, Any]:
        """Direct confirmation — bypasses text parsing."""
        session = self.sessions.get(session_id)
        if not session or not session.build_contract:
            return {"error": "Session not found or no contract"}

        session.build_contract.sign()
        session.state = SessionState.BUILDING
        return {
            "action": "build_start",
            "session_id": session_id,
            "contract_id": session.build_contract.contract_id,
            "contract_hash": session.build_contract.contract_hash,
            "message": f"Building {session.build_contract.project_name}.",
            "contract": self._serialize_contract(session.build_contract),
            "stream_url": f"/api/concierge/{session_id}/stream",
        }

    def get_session(self, session_id: str) -> Optional[ConciergeSession]:
        return self.sessions.get(session_id)

    def get_contract(self, session_id: str) -> Optional[BuildContract]:
        s = self.sessions.get(session_id)
        return s.build_contract if s else None

    def mark_building(self, session_id: str, build_id: str):
        s = self.sessions.get(session_id)
        if s:
            s.build_id = build_id
            s.state = SessionState.BUILDING

    def mark_complete(self, session_id: str):
        s = self.sessions.get(session_id)
        if s:
            s.state = SessionState.COMPLETE

    def mark_failed(self, session_id: str):
        s = self.sessions.get(session_id)
        if s:
            s.state = SessionState.FAILED

    # ──────────────────────────────────────────────────────────────────────
    # CLASSIFICATION & SCORING
    # ──────────────────────────────────────────────────────────────────────

    def _detect_mode(self, text: str, explicit: Optional[str]) -> UserMode:
        if explicit:
            try:
                return UserMode(explicit.lower())
            except ValueError:
                pass

        lower = text.lower()
        for trigger in SILENT_TRIGGERS:
            if trigger in lower:
                return UserMode.SILENT
        for trigger in VERBOSE_TRIGGERS:
            if trigger in lower:
                return UserMode.VERBOSE
        return UserMode.BALANCED

    def _classify_project(self, text: str) -> ProjectType:
        lower = text.lower()
        best_type = ProjectType.UNKNOWN
        best_count = 0
        for ptype, keywords in PROJECT_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in lower)
            if count > best_count:
                best_count = count
                best_type = ptype
        return best_type

    def _score_ambiguity(self, text: str, project_type: ProjectType) -> float:
        """
        Score from 0 (crystal clear) to 10 (total chaos).
        Checks for: specificity, features mentioned, tech mentioned, length.
        """
        score = 5.0  # Start at middle

        # Length penalty (too short = vague)
        word_count = len(text.split())
        if word_count < 5:
            score += 3.0
        elif word_count < 15:
            score += 1.5
        elif word_count > 50:
            score -= 1.5
        elif word_count > 100:
            score -= 2.5

        # Known project type reduces ambiguity
        if project_type != ProjectType.UNKNOWN:
            score -= 1.5

        # Specific tech mentions reduce ambiguity
        tech_terms = ["react", "python", "fastapi", "postgres", "mongodb", "redis",
                      "stripe", "supabase", "vercel", "render", "next.js", "typescript"]
        tech_count = sum(1 for t in tech_terms if t in text.lower())
        score -= min(tech_count * 0.5, 2.0)

        # Feature clarity
        feature_indicators = ["with", "including", "that can", "which", "should", "must", "needs to", "allows"]
        feature_count = sum(1 for f in feature_indicators if f in text.lower())
        score -= min(feature_count * 0.3, 1.5)

        # Vagueness penalty
        vague_terms = ["something", "stuff", "things", "like", "maybe", "kind of", "sort of", "etc"]
        vague_count = sum(1 for v in vague_terms if v in text.lower())
        score += min(vague_count * 0.5, 2.0)

        return max(0.0, min(10.0, score))

    # ──────────────────────────────────────────────────────────────────────
    # QUESTION GENERATION
    # ──────────────────────────────────────────────────────────────────────

    async def _generate_questions(
        self, text: str, project_type: ProjectType,
        ambiguity: float, mode: UserMode
    ) -> List[ClarifyingQuestion]:
        """
        Generate targeted clarifying questions.
        Silent mode = 0 questions.
        Balanced mode = max 3 questions.
        Verbose mode = up to 5 questions.
        """
        if mode == UserMode.SILENT:
            return []

        max_questions = 3 if mode == UserMode.BALANCED else 5
        # If ambiguity is low enough, skip all questions
        if ambiguity < 2.0:
            return []

        questions = []

        # Always ask project name if not mentioned
        if not self._has_project_name(text):
            questions.append(ClarifyingQuestion(
                question_id="project_name",
                question="What should we call this project?",
                purpose="Naming the codebase, repo, and deployment",
                options=["SaaS platform name", "API name", "App name"],
                required=True,
            ))

        # Auth question (critical for architecture)
        if not self._mentions_auth(text):
            questions.append(ClarifyingQuestion(
                question_id="auth",
                question="Does this need user authentication and accounts?",
                purpose="Auth architecture affects the entire stack",
                options=["Yes — email/password login", "Yes — social login (Google/GitHub)", "No — public access only", "Yes — enterprise SSO"],
                required=True,
            ))

        # Database question
        if project_type not in (ProjectType.LANDING_PAGE, ProjectType.CLI_TOOL) and ambiguity > 3:
            questions.append(ClarifyingQuestion(
                question_id="data",
                question="What kind of data does this store and serve?",
                purpose="Data model drives the database choice and API design",
                options=["User profiles and content", "Products and transactions", "Analytics and events", "Just config/settings"],
                required=True,
            ))

        # Deployment target
        if ambiguity > 4 and len(questions) < max_questions:
            questions.append(ClarifyingQuestion(
                question_id="deploy",
                question="Where should this deploy?",
                purpose="Deployment target determines build config and CI/CD",
                options=["Render (recommended)", "Vercel", "Railway", "Self-hosted / VPS", "AWS"],
                required=False,
            ))

        # Verbose only: payment/monetization
        if mode == UserMode.VERBOSE and len(questions) < max_questions:
            questions.append(ClarifyingQuestion(
                question_id="payments",
                question="Does this handle payments?",
                purpose="Stripe integration requires specific architecture",
                options=["Yes — one-time payments", "Yes — subscriptions", "No payments needed", "Yes — marketplace payments"],
                required=False,
            ))

        return questions[:max_questions]

    def _has_project_name(self, text: str) -> bool:
        # Simple heuristic: if there's a capitalized proper noun or quoted name
        import re
        return bool(re.search(r'"[^"]+"|\'[^\']+\'|called\s+\w+|named\s+\w+', text, re.IGNORECASE))

    def _mentions_auth(self, text: str) -> bool:
        auth_terms = ["login", "auth", "signup", "sign in", "user account", "registration", "no login", "public"]
        return any(t in text.lower() for t in auth_terms)

    # ──────────────────────────────────────────────────────────────────────
    # CONTRACT GENERATION
    # ──────────────────────────────────────────────────────────────────────

    async def _generate_contract(self, session: ConciergeSession) -> BuildContract:
        """
        Generate a structured build contract from session data.
        Uses LLM if available, otherwise uses deterministic extraction.
        """
        answers = {q.question_id: q.answer for q in session.questions if q.answered}
        project_name = answers.get("project_name") or self._extract_project_name(session.raw_input)
        tech = TECH_DEFAULTS[session.project_type].copy()
        deploy_answer = answers.get("deploy", "")
        if deploy_answer:
            tech["deploy"] = deploy_answer.split("(")[0].strip()
        auth_required = self._parse_auth_answer(answers.get("auth", ""), session.raw_input)
        database_needed = session.project_type not in (ProjectType.LANDING_PAGE, ProjectType.CLI_TOOL)

        # Generate mission + features via LLM (or fallback)
        if self.llm:
            mission, features, full_desc = await self._llm_extract_mission(session, answers)
        else:
            mission, features, full_desc = self._deterministic_extract(session, answers)

        # Estimate timeline
        complexity = len(features)
        if complexity <= 3:
            timeline = "Simple build — estimated 2-4 minutes"
        elif complexity <= 6:
            timeline = "Standard build — estimated 4-8 minutes"
        else:
            timeline = "Complex build — estimated 8-15 minutes"

        contract = BuildContract(
            contract_id=str(uuid.uuid4()),
            session_id=session.session_id,
            project_name=project_name,
            project_type=session.project_type,
            mission=mission,
            full_description=full_desc,
            user_mode=session.user_mode,
            tech_stack={k: v for k, v in tech.items() if v},
            features=features,
            auth_required=auth_required,
            database_needed=database_needed,
            deployment_target=tech.get("deploy", "Render"),
            timeline_estimate=timeline,
            questions_asked=[
                {"question": q.question, "answer": q.answer}
                for q in session.questions if q.answered
            ],
        )
        return contract

    async def _llm_extract_mission(
        self, session: ConciergeSession, answers: Dict
    ) -> Tuple[str, List[str], str]:
        """Use Claude to generate a clean mission, feature list, and description."""
        answers_text = "\n".join(f"  - {k}: {v}" for k, v in answers.items()) if answers else "  (none)"
        system = """You are Franklin, a senior software architect.
Extract a structured build specification from the user's request.

Return ONLY valid JSON in this exact format:
{
  "mission": "One sentence describing what this software does and for whom",
  "description": "2-3 sentences expanding on mission, key problem solved, target user",
  "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"]
}

Features should be specific, concrete, and buildable. Max 8 features. Min 3."""

        user = f"""User's original request:
{session.raw_input}

Project type: {session.project_type.value}
Clarifying answers:
{answers_text}

Generate the structured spec."""

        try:
            response = await self.llm(system, user, temperature=0.3, max_tokens=600)
            import re
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return (
                    data.get("mission", "Build a custom software application"),
                    data.get("features", self._default_features(session.project_type)),
                    data.get("description", session.raw_input)
                )
        except Exception as e:
            logger.warning(f"LLM contract generation failed: {e}")

        return self._deterministic_extract(session, answers)

    def _deterministic_extract(
        self, session: ConciergeSession, answers: Dict
    ) -> Tuple[str, List[str], str]:
        """Fallback: deterministic extraction without LLM."""
        mission = f"Build a {session.project_type.value.replace('_', ' ')} based on: {session.raw_input[:100]}"
        features = self._default_features(session.project_type)
        full_desc = session.raw_input
        return mission, features, full_desc

    def _default_features(self, project_type: ProjectType) -> List[str]:
        defaults = {
            ProjectType.WEB_APP:       ["User interface with responsive design", "Backend API with authentication", "Database with CRUD operations", "Search and filtering", "User dashboard"],
            ProjectType.API_SERVICE:   ["RESTful API endpoints", "Authentication middleware", "Database integration", "Input validation and error handling", "API documentation"],
            ProjectType.MOBILE_APP:    ["Native mobile UI", "API integration", "Offline support", "Push notifications", "User authentication"],
            ProjectType.CLI_TOOL:      ["Command-line interface", "Configuration file support", "Logging and error handling", "Help documentation"],
            ProjectType.AI_AGENT:      ["LLM integration", "Conversation memory", "Tool use / function calling", "Streaming responses", "Session management"],
            ProjectType.ECOMMERCE:     ["Product catalog", "Shopping cart", "Stripe payment processing", "Order management", "User accounts"],
            ProjectType.SAAS_PLATFORM: ["Multi-tenant architecture", "Subscription billing", "Admin dashboard", "User onboarding", "Analytics"],
            ProjectType.LANDING_PAGE:  ["Hero section with CTA", "Feature highlights", "Pricing section", "Waitlist/contact form", "Mobile responsive"],
            ProjectType.UNKNOWN:       ["Core application logic", "User interface", "Data persistence", "Authentication", "API integration"],
        }
        return defaults.get(project_type, defaults[ProjectType.UNKNOWN])

    def _extract_project_name(self, text: str) -> str:
        import re
        # Try quoted name
        match = re.search(r'"([^"]+)"|\'([^\']+)\'', text)
        if match:
            return match.group(1) or match.group(2)
        # Try "called X" / "named X"
        match = re.search(r'(?:called|named)\s+([A-Z]\w+|\w+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        # Default: first two capitalized words or generic
        words = [w for w in text.split() if w[0].isupper() and len(w) > 2]
        if words:
            return " ".join(words[:2])
        return "Franklin Build"

    def _parse_auth_answer(self, answer: str, raw: str) -> bool:
        if not answer:
            return "login" in raw.lower() or "auth" in raw.lower() or "user" in raw.lower()
        return answer.lower().startswith("yes") or "login" in answer.lower()

    def _parse_confirmation(self, text: str) -> bool:
        positive = {"yes", "y", "confirm", "go", "build", "start", "approved", "ok", "looks good", "ship it", "do it", "correct", "perfect"}
        lower = text.lower().strip()
        return any(p in lower for p in positive)

    # ──────────────────────────────────────────────────────────────────────
    # RESPONSE FORMATTERS
    # ──────────────────────────────────────────────────────────────────────

    def _response_ask_question(self, session: ConciergeSession) -> Dict[str, Any]:
        q = session.questions[session.current_question_idx]
        remaining = len([x for x in session.questions if not x.answered])
        total = len(session.questions)
        answered = total - remaining

        prefix = self._franklin_preamble(session, answered, total)

        return {
            "action": "question",
            "session_id": session.session_id,
            "question_id": q.question_id,
            "question": q.question,
            "purpose": q.purpose,
            "options": q.options,
            "progress": f"{answered}/{total} clarified",
            "preamble": prefix,
            "can_skip": not q.required,
        }

    def _response_contract_ready(self, session: ConciergeSession) -> Dict[str, Any]:
        c = session.build_contract
        contract_display = self._format_contract_for_display(c)
        return {
            "action": "contract_ready",
            "session_id": session.session_id,
            "contract_id": c.contract_id,
            "contract": self._serialize_contract(c),
            "display": contract_display,
            "message": f"Here's the build contract for {c.project_name}. Confirm to start building, or tell me what to change.",
        }

    def _franklin_preamble(self, session: ConciergeSession, answered: int, total: int) -> str:
        if answered == 0:
            return f"I've got your idea. Just {total} quick question{'s' if total > 1 else ''} before we lock the spec and start building."
        return f"Good. {answered} of {total} sorted."

    def _format_contract_for_display(self, c: BuildContract) -> str:
        stack_str = " | ".join(f"{k}: {v}" for k, v in c.tech_stack.items())
        features_str = "\n".join(f"  • {f}" for f in c.features)
        auth_str = "Yes" if c.auth_required else "No"
        return f"""
╔═══════════════════════════════════════════════════════════╗
║  BUILD CONTRACT — {c.project_name:<38} ║
╠═══════════════════════════════════════════════════════════╣
  Mission:    {c.mission}

  Stack:      {stack_str}
  Auth:       {auth_str}
  Deploy to:  {c.deployment_target}

  Features:
{features_str}

  Estimate:   {c.timeline_estimate}
╚═══════════════════════════════════════════════════════════╝
""".strip()

    def _serialize_contract(self, c: BuildContract) -> Dict:
        return {
            "contract_id": c.contract_id,
            "project_name": c.project_name,
            "project_type": c.project_type.value,
            "mission": c.mission,
            "description": c.full_description,
            "tech_stack": c.tech_stack,
            "features": c.features,
            "auth_required": c.auth_required,
            "database_needed": c.database_needed,
            "deployment_target": c.deployment_target,
            "timeline_estimate": c.timeline_estimate,
            "user_mode": c.user_mode.value,
            "contract_hash": c.contract_hash,
            "confirmed_at": c.confirmed_at,
        }


# ──────────────────────────────────────────────────────────────────────────────
# AUDIT CHAIN
# ──────────────────────────────────────────────────────────────────────────────

class BuildAuditChain:
    """
    Cryptographic hash chain for build audit trail.
    Each event links to the previous — tamper-evident, verifiable.
    Not a blockchain, but a verifiable chain of custody.
    """

    def __init__(self, build_id: str):
        self.build_id = build_id
        self.events: List[Dict] = []
        self.genesis_hash = hashlib.sha256(build_id.encode()).hexdigest()

    def append(self, event_type: str, data: Dict, stage: Optional[str] = None) -> str:
        """
        Append an event to the chain. Returns the event hash.
        Each event includes the previous event's hash — linked chain.
        """
        prev_hash = self.events[-1]["event_hash"] if self.events else self.genesis_hash
        event = {
            "seq": len(self.events) + 1,
            "event_type": event_type,
            "stage": stage,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prev_hash": prev_hash,
        }
        # Hash this event
        payload = json.dumps({k: v for k, v in event.items() if k != "event_hash"}, sort_keys=True)
        event["event_hash"] = hashlib.sha256(payload.encode()).hexdigest()
        self.events.append(event)
        return event["event_hash"]

    def verify(self) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of the entire chain.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        for i, event in enumerate(self.events):
            if i == 0:
                expected_prev = self.genesis_hash
            else:
                expected_prev = self.events[i - 1]["event_hash"]

            if event["prev_hash"] != expected_prev:
                errors.append(f"Chain break at seq {event['seq']}: prev_hash mismatch")

            # Recompute hash
            check_payload = json.dumps(
                {k: v for k, v in event.items() if k != "event_hash"},
                sort_keys=True
            )
            computed = hashlib.sha256(check_payload.encode()).hexdigest()
            if computed != event["event_hash"]:
                errors.append(f"Hash mismatch at seq {event['seq']}: data was tampered")

        return len(errors) == 0, errors

    def get_certificate(self) -> Dict:
        """Return the final build certificate."""
        is_valid, errors = self.verify()
        final_hash = self.events[-1]["event_hash"] if self.events else self.genesis_hash
        return {
            "build_id": self.build_id,
            "genesis_hash": self.genesis_hash,
            "final_hash": final_hash,
            "event_count": len(self.events),
            "chain_valid": is_valid,
            "errors": errors,
            "certified_at": datetime.now(timezone.utc).isoformat(),
            "certificate": hashlib.sha256(f"{self.genesis_hash}:{final_hash}:{len(self.events)}".encode()).hexdigest(),
        }

    def to_dict(self) -> Dict:
        return {
            "build_id": self.build_id,
            "genesis_hash": self.genesis_hash,
            "events": self.events,
            "certificate": self.get_certificate(),
        }


# Global singleton
_concierge: Optional[FranklinConcierge] = None


def get_concierge(llm_caller=None) -> FranklinConcierge:
    global _concierge
    if _concierge is None:
        _concierge = FranklinConcierge(llm_caller=llm_caller)
    elif llm_caller and _concierge.llm is None:
        _concierge.llm = llm_caller
    return _concierge
