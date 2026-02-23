import os
import asyncio
import csv
import hashlib
import hmac
import io
import json
import math
import random
import re
import time
import uuid
from urllib import request as urllib_request, parse as urllib_parse, error as urllib_error
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
import google.generativeai as genai
from openai import OpenAI
from pydantic import BaseModel, Field
import stripe
from supabase import create_client
from dotenv import load_dotenv
from spine.neo3 import SelfImprovementEngine, Neo3System
from spine.neo3.governance import get_governance_engine, Severity, EnforcementAction

try:
    from anthropic import Anthropic
except Exception:
    Anthropic = None

try:
    from reportlab.pdfgen import canvas
except Exception:
    canvas = None

BASE_DIR = Path(__file__).resolve().parent
MAPPING_PATH = BASE_DIR / "mapping.txt"
INDEX_PATH = BASE_DIR / "index.html"
ADMIN_PATH = BASE_DIR / "admin.html"

# Load keys
load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes")


def env_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    value = os.getenv(name, str(default))
    try:
        return float(value)
    except ValueError:
        return default


def parse_model_list(primary: str, fallback_env: str) -> List[str]:
    fallbacks = [
        value.strip()
        for value in os.getenv(fallback_env, "").split(",")
        if value.strip()
    ]
    models = [primary] + fallbacks
    return [model for idx, model in enumerate(models) if model and model not in models[:idx]]


GEMINI_KEY = os.getenv("GEMINI_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")
XAI_KEY = os.getenv("XAI_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_MISSIONS_TABLE = os.getenv("SUPABASE_MISSIONS_TABLE", "missions")
SUPABASE_AUDIT_TABLE = os.getenv("SUPABASE_AUDIT_TABLE", "audit_events")
SUPABASE_GOVERNANCE_TABLE = os.getenv(
    "SUPABASE_GOVERNANCE_TABLE", "governance_policies"
)
SUPABASE_GOVERNANCE_REVIEWS_TABLE = os.getenv(
    "SUPABASE_GOVERNANCE_REVIEWS_TABLE", "governance_reviews"
)
SUPABASE_COMPLIANCE_REVIEWS_TABLE = os.getenv(
    "SUPABASE_COMPLIANCE_REVIEWS_TABLE", "compliance_reviews"
)
SUPABASE_DOMAIN_TABLE = os.getenv("SUPABASE_DOMAIN_TABLE", "domain_profiles")
SUPABASE_DOMAIN_CERT_TABLE = os.getenv(
    "SUPABASE_DOMAIN_CERT_TABLE", "domain_certifications"
)
SUPABASE_PACKAGE_TABLE = os.getenv("SUPABASE_PACKAGE_TABLE", "knowledge_packages")
SUPABASE_DOMAIN_PACKAGE_TABLE = os.getenv("SUPABASE_DOMAIN_PACKAGE_TABLE", "domain_packages")
SUPABASE_COMPLIANCE_TEMPLATE_TABLE = os.getenv(
    "SUPABASE_COMPLIANCE_TEMPLATE_TABLE", "compliance_templates"
)
SUPABASE_DOMAIN_BADGE_TABLE = os.getenv("SUPABASE_DOMAIN_BADGE_TABLE", "domain_badges")
SUPABASE_CERT_EXAM_TABLE = os.getenv("SUPABASE_CERT_EXAM_TABLE", "certification_exams")
SUPABASE_CERT_EXAM_RESULTS_TABLE = os.getenv(
    "SUPABASE_CERT_EXAM_RESULTS_TABLE", "certification_exam_results"
)
SUPABASE_BOARD_MEMBERS_TABLE = os.getenv("SUPABASE_BOARD_MEMBERS_TABLE", "board_members")
SUPABASE_BOARD_TERMS_TABLE = os.getenv("SUPABASE_BOARD_TERMS_TABLE", "board_terms")
SUPABASE_BOARD_ASSIGNMENTS_TABLE = os.getenv(
    "SUPABASE_BOARD_ASSIGNMENTS_TABLE", "board_assignments"
)
SUPABASE_BOARD_CRITERIA_TABLE = os.getenv("SUPABASE_BOARD_CRITERIA_TABLE", "board_criteria")
SUPABASE_BOARD_SESSIONS_TABLE = os.getenv("SUPABASE_BOARD_SESSIONS_TABLE", "board_sessions")
SUPABASE_BOARD_SCORES_TABLE = os.getenv("SUPABASE_BOARD_SCORES_TABLE", "board_scores")
SUPABASE_LEDGER_EVENTS_TABLE = os.getenv("SUPABASE_LEDGER_EVENTS_TABLE", "ledger_events")
SUPABASE_LEDGER_ANCHORS_TABLE = os.getenv("SUPABASE_LEDGER_ANCHORS_TABLE", "ledger_anchors")
SUPABASE_MONTHLY_AUDITS_TABLE = os.getenv("SUPABASE_MONTHLY_AUDITS_TABLE", "monthly_audits")
SUPABASE_CONNECTORS_TABLE = os.getenv("SUPABASE_CONNECTORS_TABLE", "connectors")
SUPABASE_CONNECTOR_RUNS_TABLE = os.getenv("SUPABASE_CONNECTOR_RUNS_TABLE", "connector_runs")
SUPABASE_UPLOADS_TABLE = os.getenv("SUPABASE_UPLOADS_TABLE", "document_uploads")
SUPABASE_GOVERNANCE_PROTOCOLS_TABLE = os.getenv(
    "SUPABASE_GOVERNANCE_PROTOCOLS_TABLE", "governance_protocols"
)
SUPABASE_EVOLUTION_PLAYBOOKS_TABLE = os.getenv(
    "SUPABASE_EVOLUTION_PLAYBOOKS_TABLE", "evolution_playbooks"
)
SUPABASE_AGENT_TIERS_TABLE = os.getenv("SUPABASE_AGENT_TIERS_TABLE", "agent_tiers")
SUPABASE_BOT_TASK_TIERS_TABLE = os.getenv("SUPABASE_BOT_TASK_TIERS_TABLE", "bot_task_tiers")
SUPABASE_DOCUMENT_REGISTRY_TABLE = os.getenv(
    "SUPABASE_DOCUMENT_REGISTRY_TABLE", "document_registry"
)
SUPABASE_DOMAIN_DOCUMENT_TABLE = os.getenv(
    "SUPABASE_DOMAIN_DOCUMENT_TABLE", "domain_documents"
)
SUPABASE_DOCUMENT_TAXONOMY_TABLE = os.getenv(
    "SUPABASE_DOCUMENT_TAXONOMY_TABLE", "document_taxonomy"
)
SUPABASE_EVOLUTION_TABLE = os.getenv("SUPABASE_EVOLUTION_TABLE", "evolution_proposals")
SUPABASE_EVOLUTION_RUNS_TABLE = os.getenv(
    "SUPABASE_EVOLUTION_RUNS_TABLE", "evolution_runs"
)
SUPABASE_ACADEMY_TABLE = os.getenv("SUPABASE_ACADEMY_TABLE", "academy_modules")
SUPABASE_DEPLOYMENTS_TABLE = os.getenv("SUPABASE_DEPLOYMENTS_TABLE", "deployments")
SUPABASE_LOG_CONTEXT = env_bool("SUPABASE_LOG_CONTEXT", False)
SUPABASE_CONTEXT_LIMIT = env_int("SUPABASE_CONTEXT_LIMIT", 5000)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_SUCCESS_URL = os.getenv(
    "STRIPE_SUCCESS_URL",
    "http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
)
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "http://localhost:8000/cancel")
STRIPE_CURRENCY = os.getenv("STRIPE_CURRENCY", "usd")
STRIPE_PAYMENT_METHOD_TYPES = [
    value.strip()
    for value in os.getenv("STRIPE_PAYMENT_METHOD_TYPES", "card").split(",")
    if value.strip()
]
TRINITY_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("TRINITY_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
TRINITY_API_KEY = os.getenv("TRINITY_API_KEY")
TRINITY_RATE_LIMIT_PER_MINUTE = env_int("TRINITY_RATE_LIMIT_PER_MINUTE", 0)
TRINITY_SIGNING_SECRET = os.getenv("TRINITY_SIGNING_SECRET")
TRINITY_PROVIDER_RETRIES = env_int("TRINITY_PROVIDER_RETRIES", 1)
TRINITY_GOVERNANCE_POLICY_TTL = env_int("TRINITY_GOVERNANCE_POLICY_TTL", 120)
TRINITY_CONSENSUS_THRESHOLD = env_float("TRINITY_CONSENSUS_THRESHOLD", 0.25)
TRINITY_REQUIRE_CONSENSUS = env_bool("TRINITY_REQUIRE_CONSENSUS", True)
TRINITY_MIN_TRUST_SCORE = env_int("TRINITY_MIN_TRUST_SCORE", 70)
TRINITY_REQUIRE_VALIDATION = env_bool("TRINITY_REQUIRE_VALIDATION", True)
TRINITY_MIN_COMPLIANCE_SCORE = env_int("TRINITY_MIN_COMPLIANCE_SCORE", 80)
TRINITY_VALIDATOR_MODEL = os.getenv("TRINITY_VALIDATOR_MODEL", "gpt-4o-mini")
TRINITY_BOARD_CRITERIA_COUNT = env_int("TRINITY_BOARD_CRITERIA_COUNT", 4)
TRINITY_BOARD_SECRET = os.getenv("TRINITY_BOARD_SECRET")
TRINITY_LEDGER_VAULT_RATE = env_float("TRINITY_LEDGER_VAULT_RATE", 0.02)
TRINITY_LEDGER_REBIRTH_RATE = env_float("TRINITY_LEDGER_REBIRTH_RATE", 0.0)
TRINITY_BLOCKCHAIN_NETWORK = os.getenv("TRINITY_BLOCKCHAIN_NETWORK")
TRINITY_BLOCKCHAIN_ANCHOR_ADDRESS = os.getenv("TRINITY_BLOCKCHAIN_ANCHOR_ADDRESS")
TRINITY_DOCS_LIMIT = env_int("TRINITY_DOCS_LIMIT", 20)
TRINITY_UPLOAD_DIR = os.getenv("TRINITY_UPLOAD_DIR", str(BASE_DIR / "uploads"))
TRINITY_UPLOAD_MAX_MB = env_int("TRINITY_UPLOAD_MAX_MB", 250)
TRINITY_CONNECTOR_ALLOWLIST = [
    value.strip()
    for value in os.getenv("TRINITY_CONNECTOR_ALLOWLIST", "").split(",")
    if value.strip()
]
TRINITY_CONNECTOR_TIMEOUT = env_int("TRINITY_CONNECTOR_TIMEOUT", 30)
TRINITY_PRIMARY_PROVIDER_ORDER = [
    value.strip()
    for value in os.getenv("TRINITY_PRIMARY_PROVIDER_ORDER", "gemini,grok,claude,gpt").split(",")
    if value.strip()
]
TRINITY_KLING_EDGE_URL = os.getenv("TRINITY_KLING_EDGE_URL")

GEMINI_MODEL_PRIMARY = os.getenv("GEMINI_MODEL_PRIMARY", "gemini-3-flash")
OPENAI_MODEL_PRIMARY = os.getenv("OPENAI_MODEL_PRIMARY", "gpt-5.2")
XAI_MODEL_PRIMARY = os.getenv("XAI_MODEL_PRIMARY", "grok")
ANTHROPIC_MODEL_PRIMARY = os.getenv("ANTHROPIC_MODEL_PRIMARY", "claude-4.5")

GEMINI_MODEL_LIST = parse_model_list(GEMINI_MODEL_PRIMARY, "GEMINI_MODEL_FALLBACKS")
OPENAI_MODEL_LIST = parse_model_list(OPENAI_MODEL_PRIMARY, "OPENAI_MODEL_FALLBACKS")
XAI_MODEL_LIST = parse_model_list(XAI_MODEL_PRIMARY, "XAI_MODEL_FALLBACKS")
ANTHROPIC_MODEL_LIST = parse_model_list(
    ANTHROPIC_MODEL_PRIMARY, "ANTHROPIC_MODEL_FALLBACKS"
)

app = FastAPI(title="Trinity", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=TRINITY_ALLOWED_ORIGINS or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_model = None
gemini_models_cache: Dict[str, Any] = {}
openai_client = None
xai_client = None
anthropic_client = None
supabase_client = None
rate_limit_bucket: Dict[tuple, int] = {}
last_rate_limit_minute = -1
PUBLIC_PATHS = {"/", "/health", "/stripe/webhook"}
governance_cache: Dict[str, Any] = {"policies": [], "expires_at": 0.0}
neo3_system: Optional[Neo3System] = None
self_improvement_engine: Optional[SelfImprovementEngine] = None
self_improvement_initialized = False


def configure_clients() -> None:
    global gemini_model, openai_client, xai_client, anthropic_client, supabase_client, gemini_models_cache
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            gemini_model = genai.GenerativeModel(GEMINI_MODEL_LIST[0])
            gemini_models_cache = {GEMINI_MODEL_LIST[0]: gemini_model}
        except Exception as exc:
            print(f"Startup Warning (Gemini): {exc}")
            gemini_model = None
    if OPENAI_KEY:
        try:
            openai_client = OpenAI(api_key=OPENAI_KEY)
        except Exception as exc:
            print(f"Startup Warning (OpenAI): {exc}")
            openai_client = None
    if XAI_KEY:
        try:
            xai_client = OpenAI(api_key=XAI_KEY, base_url="https://api.x.ai/v1")
        except Exception as exc:
            print(f"Startup Warning (xAI): {exc}")
            xai_client = None
    if ANTHROPIC_KEY and Anthropic:
        try:
            anthropic_client = Anthropic(api_key=ANTHROPIC_KEY)
        except Exception as exc:
            print(f"Startup Warning (Anthropic): {exc}")
            anthropic_client = None
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        except Exception as exc:
            print(f"Startup Warning (Supabase): {exc}")
            supabase_client = None


configure_clients()


def get_gemini_model(name: str):
    if name in gemini_models_cache:
        return gemini_models_cache[name]
    model = genai.GenerativeModel(name)
    gemini_models_cache[name] = model
    return model


def is_rate_limited(client_ip: str) -> bool:
    global last_rate_limit_minute
    if TRINITY_RATE_LIMIT_PER_MINUTE <= 0:
        return False
    current_minute = int(time.time() // 60)
    if current_minute != last_rate_limit_minute:
        stale_keys = [
            key for key in rate_limit_bucket.keys() if key[1] < current_minute
        ]
        for key in stale_keys:
            rate_limit_bucket.pop(key, None)
        last_rate_limit_minute = current_minute
    key = (client_ip, current_minute)
    rate_limit_bucket[key] = rate_limit_bucket.get(key, 0) + 1
    return rate_limit_bucket[key] > TRINITY_RATE_LIMIT_PER_MINUTE


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    if TRINITY_API_KEY and request.url.path not in PUBLIC_PATHS:
        if request.headers.get("x-api-key") != TRINITY_API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized", "request_id": request_id},
            )
    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded", "request_id": request_id},
        )
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


def get_bid_rules() -> str:
    if MAPPING_PATH.exists():
        return MAPPING_PATH.read_text(encoding="utf-8")
    return "NO BID MAPPING FOUND."


def trim_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[:limit]


def require_supabase() -> None:
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase not configured.")


def require_stripe() -> None:
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured.")
    stripe.api_key = STRIPE_SECRET_KEY


def require_board_secret() -> None:
    if not TRINITY_BOARD_SECRET:
        raise HTTPException(status_code=503, detail="Board secret not configured.")


def get_neo3_system() -> Neo3System:
    global neo3_system
    if not neo3_system:
        neo3_system = Neo3System()
    if not neo3_system.initialized:
        neo3_system.initialize()
    return neo3_system


def get_self_improvement_engine() -> SelfImprovementEngine:
    global self_improvement_engine, self_improvement_initialized
    if not self_improvement_engine:
        self_improvement_engine = SelfImprovementEngine()
    if not self_improvement_initialized:
        self_improvement_engine.initialize()
        self_improvement_initialized = True
    return self_improvement_engine


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sign_payload(payload: Dict[str, Any]) -> Optional[str]:
    if not TRINITY_SIGNING_SECRET:
        return None
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        TRINITY_SIGNING_SECRET.encode("utf-8"),
        serialized.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def build_evidence(
    prompt: str,
    rules: str,
    file_hashes: Dict[str, str],
    results: Dict[str, str],
) -> Dict[str, Any]:
    evidence = {
        "prompt_hash": hash_text(prompt),
        "rules_hash": hash_text(rules),
        "file_hashes": file_hashes,
        "output_hashes": {key: hash_text(value) for key, value in results.items()},
        "generated_at": utc_now_iso(),
    }
    signature = sign_payload(evidence)
    if signature:
        evidence["signature"] = signature
    return evidence


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value or "")
    cleaned = cleaned.strip("._")
    return cleaned or "upload"


def ensure_upload_dir() -> Path:
    path = Path(TRINITY_UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload(file: UploadFile) -> Tuple[str, Path, int, str]:
    upload_id = str(uuid.uuid4())
    safe_name = safe_filename(file.filename or "upload.bin")
    upload_dir = ensure_upload_dir()
    file_path = upload_dir / f"{upload_id}_{safe_name}"
    size = 0
    digest = hashlib.sha256()
    chunk_size = 1024 * 1024
    max_bytes = TRINITY_UPLOAD_MAX_MB * 1024 * 1024 if TRINITY_UPLOAD_MAX_MB > 0 else None

    try:
        with open(file_path, "wb") as handle:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                size += len(chunk)
                if max_bytes and size > max_bytes:
                    raise HTTPException(status_code=413, detail="Upload exceeds max size.")
                digest.update(chunk)
                handle.write(chunk)
    except Exception:
        if file_path.exists():
            file_path.unlink()
        raise
    finally:
        await file.close()

    return upload_id, file_path, size, digest.hexdigest()


def serialize_csv_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    if value is None:
        return ""
    return str(value)


def rows_to_csv(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return ""
    fieldnames = sorted({key for row in rows for key in row.keys()})
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: serialize_csv_value(row.get(key)) for key in fieldnames})
    return output.getvalue()


def render_pdf(title: str, rows: List[Dict[str, Any]]) -> bytes:
    if canvas is None:
        raise HTTPException(status_code=501, detail="PDF export unavailable. Install reportlab.")
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica", 12)
    y = 800
    pdf.drawString(40, y, title)
    y -= 20
    for row in rows:
        line = json.dumps(row, sort_keys=True, ensure_ascii=True)
        if len(line) > 120:
            line = f"{line[:117]}..."
        pdf.drawString(40, y, line)
        y -= 14
        if y < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 800
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def build_csv_response(filename: str, rows: List[Dict[str, Any]]) -> Response:
    csv_body = rows_to_csv(rows)
    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def build_pdf_response(filename: str, title: str, rows: List[Dict[str, Any]]) -> Response:
    pdf_body = render_pdf(title, rows)
    return Response(
        content=pdf_body,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def truncate_payload(value: Any, limit: int = 5000) -> Any:
    if isinstance(value, (dict, list)):
        raw = json.dumps(value, sort_keys=True)
        if len(raw) > limit:
            return {"truncated": True, "preview": raw[:limit]}
        return value
    if isinstance(value, str) and len(value) > limit:
        return {"truncated": True, "preview": value[:limit]}
    return value


def is_allowed_edge_url(url: str) -> bool:
    if not TRINITY_CONNECTOR_ALLOWLIST:
        return True
    return any(url.startswith(prefix) for prefix in TRINITY_CONNECTOR_ALLOWLIST)


def is_provider_error(text: str) -> bool:
    if not text:
        return True
    lower = text.lower()
    return (
        lower.startswith("gemini error:")
        or lower.startswith("gpt error:")
        or lower.startswith("grok error:")
        or lower.startswith("claude error:")
    )


def select_primary_output(outputs: Dict[str, str], order: List[str]) -> Dict[str, Any]:
    for provider in order:
        value = outputs.get(provider) or ""
        if value and not is_provider_error(value):
            return {"provider": provider, "output": value}
    for provider, value in outputs.items():
        if value and not is_provider_error(value):
            return {"provider": provider, "output": value}
    return {"provider": order[0] if order else "unknown", "output": ""}


def build_edge_url(base: str, path: Optional[str], query: Optional[Dict[str, Any]]) -> str:
    base_url = base.rstrip("/") + "/"
    target = urllib_parse.urljoin(base_url, (path or "").lstrip("/"))
    if query:
        target = f"{target}?{urllib_parse.urlencode(query, doseq=True)}"
    return target


def should_retry(result: str) -> bool:
    lower = result.lower()
    if "not configured" in lower:
        return False
    return (
        lower.startswith("gemini error:")
        or lower.startswith("gpt error:")
        or lower.startswith("grok error:")
        or lower.startswith("claude error:")
    )


async def call_with_retry(call_fn, prompt: str) -> str:
    attempt = 0
    while True:
        result = await call_fn(prompt)
        if attempt >= TRINITY_PROVIDER_RETRIES or not should_retry(result):
            return result
        attempt += 1
        await asyncio.sleep(0.5 * attempt)


async def get_governance_policies() -> List[Dict[str, Any]]:
    if not supabase_client:
        return []
    now = time.time()
    if governance_cache["policies"] and governance_cache["expires_at"] > now:
        return governance_cache["policies"]

    def _select():
        return (
            supabase_client.table(SUPABASE_GOVERNANCE_TABLE)
            .select("*")
            .eq("enabled", True)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        policies = getattr(response, "data", []) or []
        governance_cache["policies"] = policies
        governance_cache["expires_at"] = now + TRINITY_GOVERNANCE_POLICY_TTL
        return policies
    except Exception as exc:
        print(f"Supabase Warning (governance): {exc}")
        return []


def evaluate_governance(
    outputs: Dict[str, str],
    policies: List[Dict[str, Any]],
) -> Dict[str, Any]:
    violations = []
    provider_errors = {}
    for name, text in outputs.items():
        lower = (text or "").lower()
        is_error = (
            not text
            or lower.startswith("gemini error:")
            or lower.startswith("gpt error:")
            or lower.startswith("grok error:")
            or lower.startswith("claude error:")
        )
        if is_error:
            provider_errors[name] = text or "empty response"
            violations.append(
                {
                    "policy": "provider_error",
                    "scope": name,
                    "severity": "high",
                    "detail": text[:200] if text else "empty response",
                }
            )

    for policy in policies:
        pattern = policy.get("pattern")
        if not pattern:
            continue
        scope = (policy.get("scope") or "all").lower()
        targets = outputs if scope == "all" else {scope: outputs.get(scope, "")}
        for target, text in targets.items():
            if not text:
                continue
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append(
                        {
                            "policy_id": policy.get("id"),
                            "policy": policy.get("name"),
                            "scope": target,
                            "severity": policy.get("severity", "medium"),
                        }
                    )
            except re.error:
                continue

    score = max(0, 100 - len(violations) * 10)
    status = "pass" if not violations else "review"
    return {
        "status": status,
        "score": score,
        "violations": violations,
        "provider_errors": provider_errors,
    }


def tokenize_text(text: str) -> List[str]:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return [token for token in cleaned.split() if token]


def jaccard_similarity(text_a: str, text_b: str) -> float:
    tokens_a = set(tokenize_text(text_a))
    tokens_b = set(tokenize_text(text_b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(intersection) / len(union)


def compute_cross_validation(outputs: Dict[str, str], threshold: float) -> Dict[str, Any]:
    keys = [key for key in outputs.keys() if outputs.get(key)]
    pairs: List[Tuple[str, str]] = []
    for idx, left in enumerate(keys):
        for right in keys[idx + 1 :]:
            pairs.append((left, right))
    scores: Dict[str, float] = {}
    for a, b in pairs:
        scores[f"{a}_{b}"] = jaccard_similarity(
            outputs.get(a, "") or "", outputs.get(b, "") or ""
        )
    average_similarity = sum(scores.values()) / len(scores) if scores else 0.0
    consensus = average_similarity >= threshold
    return {
        "scores": scores,
        "average_similarity": round(average_similarity, 4),
        "consensus": consensus,
        "threshold": threshold,
    }


def compute_trust_score(
    outputs: Dict[str, str],
    governance_summary: Dict[str, Any],
    cross_validation: Dict[str, Any],
) -> Dict[str, Any]:
    score = 100
    reasons = []

    provider_errors = governance_summary.get("provider_errors", {})
    if provider_errors:
        penalty = 15 * len(provider_errors)
        score -= penalty
        reasons.append(f"provider_errors:{len(provider_errors)} (-{penalty})")

    if not cross_validation.get("consensus", True):
        score -= 20
        reasons.append("low_consensus (-20)")

    short_outputs = [
        name for name, text in outputs.items() if text and len(text.strip()) < 80
    ]
    if short_outputs:
        score -= 10
        reasons.append("short_outputs (-10)")

    violations = governance_summary.get("violations", [])
    if violations:
        penalty = min(30, len(violations) * 5)
        score -= penalty
        reasons.append(f"policy_violations:{len(violations)} (-{penalty})")

    score = max(0, min(100, score))

    if score >= 90 and governance_summary.get("status") == "pass" and cross_validation.get(
        "consensus", True
    ):
        certification = "platinum"
    elif score >= 80:
        certification = "gold"
    elif score >= 70:
        certification = "silver"
    else:
        certification = "review"

    return {"score": score, "certification": certification, "reasons": reasons}


def normalize_compliance_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    status = summary.get("status", "review")
    score = summary.get("score", 0)
    findings = summary.get("findings") or summary.get("violations") or []
    rationale = summary.get("rationale") or summary.get("summary")
    return {
        "status": status,
        "score": score,
        "findings": findings,
        "rationale": rationale,
        "required_actions": summary.get("required_actions") or [],
        "citations_needed": bool(summary.get("citations_needed", False)),
        "raw": summary.get("raw"),
    }


def build_board_commit(payload: Dict[str, Any]) -> str:
    require_board_secret()
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hash_text(f"{serialized}:{TRINITY_BOARD_SECRET}")


def build_board_criteria_payload(
    criteria: List[dict],
    seed: str,
    count: int,
) -> Dict[str, Any]:
    if not criteria:
        return {"criteria": [], "weights": {}}
    rng = random.Random(seed)
    count = min(max(1, count), len(criteria))
    selected = rng.sample(criteria, count)
    weights = [rng.random() for _ in selected]
    total = sum(weights) or 1.0
    normalized = [round((w / total) * 100, 2) for w in weights]
    return {
        "criteria": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "category": item.get("category"),
            }
            for item in selected
        ],
        "weights": {
            item.get("name"): weight for item, weight in zip(selected, normalized)
        },
    }


async def run_compliance_validator(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not openai_client:
        return {
            "status": "review",
            "score": 0,
            "findings": ["validator_not_configured"],
            "rationale": "OPENAI_KEY not configured.",
        }
    templates = (payload.get("domain") or {}).get("compliance_templates") or []
    instructions = " ".join(
        [template.get("validator_instructions", "") for template in templates if template]
    )
    system_prompt = (
        "You are an enterprise compliance validator. "
        "Return STRICT JSON with keys: status (pass|review), score (0-100), "
        "findings (array), required_actions (array), citations_needed (boolean), "
        "rationale (string). Focus on legal, compliance, safety, and hallucination risk. "
        "Apply any policy_rules, compliance_templates, and domain certifications supplied. "
        f"{instructions}"
    )

    def _call():
        return openai_client.chat.completions.create(
            model=TRINITY_VALIDATOR_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=True)},
            ],
            temperature=0.1,
        )

    try:
        response = await asyncio.to_thread(_call)
        content = response.choices[0].message.content or ""
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {
                "status": "review",
                "score": 0,
                "findings": ["invalid_validator_response"],
                "rationale": "Validator returned non-JSON output.",
                "raw": content[:2000],
            }
        return normalize_compliance_summary(parsed)
    except Exception as exc:
        return {
            "status": "review",
            "score": 0,
            "findings": ["validator_error"],
            "rationale": str(exc),
        }


async def supabase_insert(table: str, payload: dict) -> Optional[dict]:
    if not supabase_client:
        return None

    def _insert():
        return supabase_client.table(table).insert(payload).execute()

    try:
        response = await asyncio.to_thread(_insert)
        data = getattr(response, "data", None)
        if data:
            return data[0]
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
    return None


async def supabase_update(table: str, match: dict, payload: dict) -> Optional[dict]:
    if not supabase_client:
        return None

    def _update():
        query = supabase_client.table(table).update(payload)
        for key, value in match.items():
            query = query.eq(key, value)
        return query.execute()

    try:
        response = await asyncio.to_thread(_update)
        data = getattr(response, "data", None)
        if data:
            return data[0]
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
    return None


async def supabase_fetch_single(table: str, match: dict) -> Optional[dict]:
    if not supabase_client:
        return None

    def _select():
        query = supabase_client.table(table).select("*").limit(1)
        for key, value in match.items():
            query = query.eq(key, value)
        return query.execute()

    try:
        response = await asyncio.to_thread(_select)
        data = getattr(response, "data", None)
        if data:
            return data[0]
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
    return None


async def fetch_table_rows(table: str, limit: int = 500) -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(table)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


async def fetch_domain_profile(domain_id: Optional[str], domain_name: Optional[str]) -> Optional[dict]:
    if not supabase_client:
        return None
    if domain_id:
        return await supabase_fetch_single(SUPABASE_DOMAIN_TABLE, {"id": domain_id})
    if domain_name:
        return await supabase_fetch_single(SUPABASE_DOMAIN_TABLE, {"name": domain_name})
    return None


async def fetch_domain_certifications(domain_id: str, limit: int = 5) -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(SUPABASE_DOMAIN_CERT_TABLE)
            .select("*")
            .eq("domain_id", domain_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


def get_domain_thresholds(domain_profile: Optional[dict]) -> Dict[str, Any]:
    if not domain_profile:
        return {
            "consensus": TRINITY_CONSENSUS_THRESHOLD,
            "trust": TRINITY_MIN_TRUST_SCORE,
            "compliance": TRINITY_MIN_COMPLIANCE_SCORE,
        }
    return {
        "consensus": float(domain_profile.get("consensus_threshold", TRINITY_CONSENSUS_THRESHOLD)),
        "trust": int(domain_profile.get("trust_threshold", TRINITY_MIN_TRUST_SCORE)),
        "compliance": int(domain_profile.get("compliance_threshold", TRINITY_MIN_COMPLIANCE_SCORE)),
    }


async def fetch_domain_packages(domain_id: str, limit: int = 10) -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(SUPABASE_DOMAIN_PACKAGE_TABLE)
            .select("*")
            .eq("domain_id", domain_id)
            .order("priority")
            .limit(limit)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


async def fetch_domain_badges(domain_id: str, limit: int = 10) -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(SUPABASE_DOMAIN_BADGE_TABLE)
            .select("*")
            .eq("domain_id", domain_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


async def fetch_domain_templates(domain_id: str, limit: int = 10) -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(SUPABASE_COMPLIANCE_TEMPLATE_TABLE)
            .select("*")
            .eq("domain_id", domain_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


async def fetch_domain_documents(domain_id: str, limit: int) -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(SUPABASE_DOMAIN_DOCUMENT_TABLE)
            .select("*")
            .eq("domain_id", domain_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


async def fetch_document_taxonomy(document_id: str, limit: int = 50) -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(SUPABASE_DOCUMENT_TAXONOMY_TABLE)
            .select("*")
            .eq("document_id", document_id)
            .order("confidence", desc=True)
            .limit(limit)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


async def fetch_active_board_criteria() -> List[dict]:
    if not supabase_client:
        return []

    def _select():
        return (
            supabase_client.table(SUPABASE_BOARD_CRITERIA_TABLE)
            .select("*")
            .eq("is_active", True)
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return getattr(response, "data", []) or []
    except Exception as exc:
        print(f"Supabase Warning: {exc}")
        return []


async def record_evolution_run(payload: dict) -> Optional[dict]:
    if not supabase_client:
        return None
    return await supabase_insert(SUPABASE_EVOLUTION_RUNS_TABLE, payload)


async def record_ledger_event(
    event_type: str,
    amount_cents: int = 0,
    currency: Optional[str] = None,
    mission_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[dict]:
    if not supabase_client:
        return None
    payload = {
        "event_type": event_type,
        "amount_cents": amount_cents,
        "currency": currency,
        "mission_id": mission_id,
        "metadata": metadata or {},
    }
    payload["event_hash"] = hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return await supabase_insert(SUPABASE_LEDGER_EVENTS_TABLE, payload)


async def create_audit_event(mission_id: str, event_type: str, payload: dict) -> None:
    if not supabase_client:
        return
    await supabase_insert(
        SUPABASE_AUDIT_TABLE,
        {
            "mission_id": mission_id,
            "event_type": event_type,
            "payload": payload,
        },
    )


async def create_governance_review(mission_id: str, summary: dict) -> None:
    if not supabase_client:
        return
    await supabase_insert(
        SUPABASE_GOVERNANCE_REVIEWS_TABLE,
        {
            "mission_id": mission_id,
            "status": summary.get("status"),
            "score": summary.get("score"),
            "violations": summary.get("violations"),
            "summary": summary,
        },
    )


async def create_compliance_review(mission_id: str, summary: dict) -> None:
    if not supabase_client:
        return
    await supabase_insert(
        SUPABASE_COMPLIANCE_REVIEWS_TABLE,
        {
            "mission_id": mission_id,
            "status": summary.get("status"),
            "score": summary.get("score"),
            "findings": summary.get("findings"),
            "summary": summary,
        },
    )


class BriefingRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    domain_id: Optional[str] = None
    domain_name: Optional[str] = None


class QuoteRequest(BaseModel):
    mission_id: str
    complexity_override: Optional[int] = None


class CheckoutRequest(BaseModel):
    mission_id: str


class GovernancePolicyRequest(BaseModel):
    name: str = Field(..., min_length=1)
    pattern: str = Field(..., min_length=1)
    severity: Optional[str] = "medium"
    scope: Optional[str] = "all"
    enabled: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None


class GovernanceReviewRequest(BaseModel):
    mission_id: str


class GovernanceProtocolRequest(BaseModel):
    name: str = Field(..., min_length=1)
    cadence: Optional[str] = None
    scope: Optional[str] = None
    description: Optional[str] = None
    human_roles: Optional[List[str]] = None
    ai_roles: Optional[List[str]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    evidence_requirements: Optional[Dict[str, Any]] = None
    escalation: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class EvolutionProposalRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    rationale: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class EvolutionPlaybookRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    stages: Optional[List[Dict[str, Any]]] = None
    guardrails: Optional[Dict[str, Any]] = None
    required_metrics: Optional[Dict[str, Any]] = None
    approval_chain: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AcademyModuleRequest(BaseModel):
    title: str = Field(..., min_length=1)
    summary: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = "active"
    content: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DeploymentRequest(BaseModel):
    version: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[str] = None
    artifacts: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class AgentTierRequest(BaseModel):
    name: str = Field(..., min_length=1)
    tier_level: Optional[int] = None
    description: Optional[str] = None
    min_usd: Optional[int] = None
    max_usd: Optional[int] = None
    required_certifications: Optional[List[str]] = None
    required_badges: Optional[List[str]] = None
    autonomy_level: Optional[str] = None
    allowed_domains: Optional[List[str]] = None
    review_requirements: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BotTaskTierRequest(BaseModel):
    name: str = Field(..., min_length=1)
    tier_level: Optional[int] = None
    description: Optional[str] = None
    min_usd: Optional[int] = None
    max_usd: Optional[int] = None
    allowed_sources: Optional[List[str]] = None
    task_types: Optional[List[str]] = None
    risk_controls: Optional[List[str]] = None
    evidence_requirements: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConnectorRequest(BaseModel):
    name: str = Field(..., min_length=1)
    connector_type: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: Optional[str] = "inactive"
    edge_url: Optional[str] = None
    scopes: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConnectorUpdateRequest(BaseModel):
    name: Optional[str] = None
    connector_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    edge_url: Optional[str] = None
    scopes: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConnectorInvokeRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    path: Optional[str] = None
    method: Optional[str] = "POST"
    query: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class DomainProfileRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    compliance_threshold: Optional[int] = Field(80, ge=0, le=100)
    trust_threshold: Optional[int] = Field(70, ge=0, le=100)
    consensus_threshold: Optional[float] = Field(0.25, ge=0.0, le=1.0)
    required_certifications: Optional[List[str]] = None
    policy_tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DomainCertificationRequest(BaseModel):
    agent_name: str = Field(..., min_length=1)
    certification_level: str = Field(..., min_length=1)
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class KnowledgePackageRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DomainPackageLinkRequest(BaseModel):
    package_id: str = Field(..., min_length=1)
    role: Optional[str] = "reference"
    priority: Optional[int] = 1
    metadata: Optional[Dict[str, Any]] = None


class ComplianceTemplateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    validator_instructions: Optional[str] = None
    policy_rules: Optional[List[str]] = None
    severity: Optional[str] = "high"
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DomainBadgeRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    level: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CertificationExamRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    pass_score: Optional[int] = Field(85, ge=0, le=100)
    certification_level: Optional[str] = None
    rubric: Optional[Dict[str, Any]] = None
    questions: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class CertificationExamSubmissionRequest(BaseModel):
    agent_name: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    details: Optional[Dict[str, Any]] = None


class BoardMemberRequest(BaseModel):
    name: str = Field(..., min_length=1)
    member_type: str = Field(..., min_length=1)
    role: Optional[str] = None
    active: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None


class BoardTermRequest(BaseModel):
    term_label: str = Field(..., min_length=1)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = "active"
    metadata: Optional[Dict[str, Any]] = None


class BoardAssignmentRequest(BaseModel):
    member_id: str = Field(..., min_length=1)
    seat: Optional[str] = None
    responsibility: Optional[str] = None
    active: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None


class BoardCriteriaRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: Optional[str] = None
    weight_default: Optional[int] = None
    is_active: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None


class BoardSessionRequest(BaseModel):
    term_id: Optional[str] = None
    mission_id: Optional[str] = None
    domain_id: Optional[str] = None
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BoardScoreRequest(BaseModel):
    member_id: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None
    criteria_scores: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class LedgerEventRequest(BaseModel):
    event_type: str = Field(..., min_length=1)
    amount_cents: Optional[int] = 0
    currency: Optional[str] = None
    mission_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LedgerAnchorRequest(BaseModel):
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LedgerAnchorFinalizeRequest(BaseModel):
    tx_hash: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class MonthlyAuditRequest(BaseModel):
    month_label: str = Field(..., min_length=1)
    summary: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class EvolutionRunRequest(BaseModel):
    iterations: int = Field(10, ge=1, le=100)


class Neo3ProcessRequest(BaseModel):
    input_data: Any = Field(...)


class Neo3TrainRequest(BaseModel):
    training_data: List[Dict[str, Any]]


class Neo3EvolveRequest(BaseModel):
    iterations: int = Field(1, ge=1, le=50)


def estimate_quote(
    prompt: str,
    context: Optional[str],
    file_count: int,
    complexity_override: Optional[int] = None,
) -> Dict[str, Any]:
    base_cents = 5000
    per_unit_cents = 2000
    if complexity_override is not None:
        complexity_score = complexity_override
    else:
        complexity_score = len(prompt) + len(context or "") + (file_count * 1000)
    units = max(1, math.ceil(complexity_score / 1500))
    total_cents = base_cents + (units - 1) * per_unit_cents
    return {
        "total_cents": total_cents,
        "currency": STRIPE_CURRENCY,
        "breakdown": {
            "base_cents": base_cents,
            "per_unit_cents": per_unit_cents,
            "units": units,
            "complexity_score": complexity_score,
            "file_count": file_count,
        },
    }


async def run_execution(
    prompt: str,
    file_context: str,
    file_names: List[str],
    file_hashes: Dict[str, str],
    mission_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    domain_name: Optional[str] = None,
    run_reason: str = "execution",
) -> Dict[str, Any]:
    # Execution contract (API boundary):
    # - Accepts: prompt + file context + optional mission/domain identifiers.
    # - Guarantees: governance enforcement is fail-closed and audited.
    # - Refuses: missing prompt, isolated industry, replay, failed governance checks.
    governance_engine = get_governance_engine()
    execution_id = (
        f"{mission_id}:{uuid.uuid4()}" if mission_id else str(uuid.uuid4())
    )
    industry_key = governance_engine.resolve_industry_key(domain_name or domain_id)
    responsible_agent = governance_engine.resolve_responsible_agent(
        industry_key,
        metadata={"mission_id": mission_id, "domain_id": domain_id, "domain_name": domain_name},
    )
    master_rules = get_bid_rules()
    god_prompt = f"""
[BID MAPPING / RULES]
{master_rules}

[PROJECT FILES]
{file_context}

[USER COMMAND]
{prompt}
"""

    try:
        allowed, enforcement = governance_engine.guard_execution_id(
            execution_id,
            industry_key,
            responsible_agent,
            metadata={
                "execution_id": execution_id,
                "mission_id": mission_id,
                "run_reason": run_reason,
                "domain_id": domain_id,
                "domain_name": domain_name,
            },
        )
    except Exception:
        enforcement = governance_engine.enforce(
            Severity.ORANGE,
            industry_key,
            responsible_agent,
            "Governance replay guard error.",
            metadata={
                "execution_id": execution_id,
                "mission_id": mission_id,
                "run_reason": run_reason,
                "domain_id": domain_id,
                "domain_name": domain_name,
            },
            reason_code="internal_error",
        )
        blocked_outputs = {
            provider: "Execution blocked: governance replay guard error."
            for provider in TRINITY_PRIMARY_PROVIDER_ORDER
        }
        governance_summary = {
            "status": "halted",
            "enforcement": enforcement.__dict__,
            "reason": "Governance replay guard error.",
        }
        if supabase_client and mission_id:
            await supabase_update(
                SUPABASE_MISSIONS_TABLE,
                {"id": mission_id},
                {"status": "review", "governance": governance_summary},
            )
            await create_audit_event(
                mission_id,
                "governance_enforced",
                {"enforcement": enforcement.__dict__},
            )
        return {
            "outputs": blocked_outputs,
            "evidence": {"status": "blocked", "execution_id": execution_id},
            "governance": governance_summary,
        }
    if not allowed:
        blocked_outputs = {
            provider: f"Execution blocked: replay detected for '{execution_id}'."
            for provider in TRINITY_PRIMARY_PROVIDER_ORDER
        }
        governance_summary = {
            "status": "halted",
            "enforcement": enforcement.__dict__ if enforcement else {},
            "reason": "Replay detected.",
        }
        if supabase_client and mission_id:
            await supabase_update(
                SUPABASE_MISSIONS_TABLE,
                {"id": mission_id},
                {"status": "review", "governance": governance_summary},
            )
            await create_audit_event(
                mission_id,
                "governance_enforced",
                {"enforcement": enforcement.__dict__ if enforcement else {}},
            )
        return {
            "outputs": blocked_outputs,
            "evidence": {"status": "blocked", "execution_id": execution_id},
            "governance": governance_summary,
        }

    if governance_engine.is_industry_isolated(industry_key):
        isolation = governance_engine.get_industry_isolation(industry_key) or {}
        severity_value = isolation.get("severity", Severity.RED.value)
        try:
            severity = Severity(severity_value)
        except ValueError:
            severity = Severity.RED
        enforcement = governance_engine.enforce(
            severity,
            industry_key,
            responsible_agent,
            f"Execution blocked: {isolation.get('reason', 'Industry isolated.')}",
            metadata={
                "execution_id": execution_id,
                "mission_id": mission_id,
                "run_reason": run_reason,
                "domain_id": domain_id,
                "domain_name": domain_name,
            },
            reason_code="industry_isolated",
        )
        blocked_outputs = {
            provider: f"Execution blocked: industry '{industry_key}' in safe mode."
            for provider in TRINITY_PRIMARY_PROVIDER_ORDER
        }
        governance_summary = {
            "status": "halted",
            "enforcement": enforcement.__dict__,
            "reason": "Industry isolated.",
        }
        if supabase_client and mission_id:
            await supabase_update(
                SUPABASE_MISSIONS_TABLE,
                {"id": mission_id},
                {"status": "review", "governance": governance_summary},
            )
            await create_audit_event(
                mission_id,
                "governance_enforced",
                {"enforcement": enforcement.__dict__},
            )
        return {
            "outputs": blocked_outputs,
            "evidence": {"status": "blocked", "industry": industry_key},
            "governance": governance_summary,
        }

    if mission_id and supabase_client:
        await supabase_update(
            SUPABASE_MISSIONS_TABLE,
            {"id": mission_id},
            {"status": "executing"},
        )
        await create_audit_event(
            mission_id,
            "execution_started",
            {"file_count": len(file_names), "reason": run_reason},
        )

    results = await asyncio.gather(
        call_with_retry(call_gemini, god_prompt),
        call_with_retry(call_gpt, god_prompt),
        call_with_retry(call_grok, god_prompt),
        call_with_retry(call_claude, god_prompt),
    )
    output_map = {
        "gemini": results[0],
        "gpt": results[1],
        "grok": results[2],
        "claude": results[3],
    }
    evidence = build_evidence(prompt, master_rules, file_hashes, output_map)
    policies = await get_governance_policies()
    governance_summary = evaluate_governance(output_map, policies)
    primary_choice = select_primary_output(output_map, TRINITY_PRIMARY_PROVIDER_ORDER)
    governance_summary["primary_provider"] = primary_choice["provider"]
    governance_summary["primary_output"] = trim_text(primary_choice["output"], 2000)
    domain_profile = None
    domain_certifications: List[dict] = []
    domain_packages: List[dict] = []
    domain_badges: List[dict] = []
    domain_templates: List[dict] = []
    domain_documents: List[dict] = []
    if supabase_client:
        mission_meta = (mission or {}).get("metadata") or {}
        domain_profile = await fetch_domain_profile(
            domain_id or mission_meta.get("domain_id"),
            domain_name or mission_meta.get("domain_name"),
        )
        if domain_profile and domain_profile.get("id"):
            domain_certifications = await fetch_domain_certifications(domain_profile["id"])
            domain_packages = await fetch_domain_packages(domain_profile["id"])
            domain_badges = await fetch_domain_badges(domain_profile["id"])
            domain_templates = await fetch_domain_templates(domain_profile["id"])
            domain_documents = await fetch_domain_documents(
                domain_profile["id"], TRINITY_DOCS_LIMIT
            )
    domain_thresholds = get_domain_thresholds(domain_profile)
    cross_validation = compute_cross_validation(output_map, domain_thresholds["consensus"])
    trust_summary = compute_trust_score(output_map, governance_summary, cross_validation)
    governance_summary["cross_validation"] = cross_validation
    governance_summary["trust_score"] = trust_summary["score"]
    governance_summary["certification"] = trust_summary["certification"]
    governance_summary["trust_reasons"] = trust_summary["reasons"]
    compliance_payload = {
        "prompt": prompt,
        "rules": master_rules,
        "outputs": output_map,
        "cross_validation": cross_validation,
        "governance": governance_summary,
        "domain": {
            "profile": domain_profile or {},
            "certifications": domain_certifications,
            "packages": domain_packages,
            "badges": domain_badges,
            "compliance_templates": domain_templates,
            "documents": domain_documents,
        },
        "metadata": {"file_count": len(file_names), "has_files": bool(file_names)},
    }
    compliance_summary = await run_compliance_validator(compliance_payload)
    compliance_summary["signature"] = sign_payload(compliance_summary)
    governance_summary["compliance"] = compliance_summary
    governance_summary["domain"] = {
        "profile": domain_profile,
        "thresholds": domain_thresholds,
        "certifications": domain_certifications,
        "packages": domain_packages,
        "badges": domain_badges,
        "compliance_templates": domain_templates,
        "documents": domain_documents,
    }
    rule_ids = []
    for violation in governance_summary.get("violations", []) or []:
        rule_id = violation.get("policy_id") or violation.get("policy")
        if rule_id:
            rule_ids.append(str(rule_id))
    rule_ids = sorted({rule_id for rule_id in rule_ids})
    industry_key = governance_engine.resolve_industry_key(
        domain_name or (domain_profile or {}).get("name") or domain_id
    )
    responsible_agent = governance_engine.resolve_responsible_agent(
        industry_key,
        metadata={"mission_id": mission_id, "domain_id": domain_id, "domain_name": domain_name},
        domain_profile=domain_profile or {},
    )
    classification = governance_engine.classify_execution(
        governance_summary, compliance_summary, domain_thresholds
    )
    enforcement = governance_engine.enforce(
        classification["severity"],
        industry_key,
        responsible_agent,
        classification["reason"],
        metadata={
            "execution_id": execution_id,
            "mission_id": mission_id,
            "run_reason": run_reason,
            "domain_id": domain_id,
            "domain_name": domain_name,
            "rule_ids": rule_ids,
        },
        reason_code="governance_classified",
        action_override=EnforcementAction.ALLOW,
    )
    governance_summary["enforcement"] = enforcement.__dict__
    if enforcement.action == "halt_and_fork":
        governance_summary["status"] = "halted"
    if governance_summary["status"] != "halted":
        if TRINITY_REQUIRE_CONSENSUS and not cross_validation["consensus"]:
            governance_summary["status"] = "review"
        if trust_summary["score"] < domain_thresholds["trust"]:
            governance_summary["status"] = "review"
        if TRINITY_REQUIRE_VALIDATION:
            if compliance_summary["status"] != "pass":
                governance_summary["status"] = "review"
            if compliance_summary["score"] < domain_thresholds["compliance"]:
                governance_summary["status"] = "review"
    final_status = "completed" if governance_summary["status"] == "pass" else "review"

    payload = {
        "prompt": prompt,
        "file_names": file_names,
        "gemini": results[0],
        "gpt": results[1],
        "grok": results[2],
        "claude": results[3],
        "evidence": evidence,
        "governance": governance_summary,
        "status": final_status,
        "completed_at": utc_now_iso(),
        "metadata": {
            "file_count": len(file_names),
            "has_files": bool(file_names),
            "run_reason": run_reason,
            "domain_id": domain_id or (domain_profile or {}).get("id"),
            "domain_name": domain_name or (domain_profile or {}).get("name"),
        },
    }
    if SUPABASE_LOG_CONTEXT and file_context:
        payload["file_context"] = trim_text(file_context, SUPABASE_CONTEXT_LIMIT)

    if supabase_client:
        if mission_id:
            mission = await supabase_fetch_single(
                SUPABASE_MISSIONS_TABLE, {"id": mission_id}
            )
            existing_metadata = (mission or {}).get("metadata") or {}
            payload["metadata"] = {**existing_metadata, **payload["metadata"]}
            await supabase_update(SUPABASE_MISSIONS_TABLE, {"id": mission_id}, payload)
            await create_audit_event(
                mission_id,
                "execution_completed",
                {"evidence_hash": evidence["output_hashes"]},
            )
            await create_governance_review(mission_id, governance_summary)
            await create_compliance_review(mission_id, compliance_summary)
            await create_audit_event(
                mission_id,
                "assurance_scored",
                {
                    "trust_score": trust_summary["score"],
                    "certification": trust_summary["certification"],
                    "consensus": cross_validation["consensus"],
                    "compliance_score": compliance_summary["score"],
                    "compliance_status": compliance_summary["status"],
                },
            )
            await create_audit_event(
                mission_id,
                "governance_enforced",
                {"enforcement": enforcement.__dict__},
            )
            await record_ledger_event(
                "mission_completed",
                amount_cents=0,
                currency=None,
                mission_id=mission_id,
                metadata={
                    "certification": trust_summary["certification"],
                    "trust_score": trust_summary["score"],
                    "compliance_score": compliance_summary["score"],
                },
            )
        else:
            mission = await supabase_insert(SUPABASE_MISSIONS_TABLE, payload)
            if mission:
                await create_audit_event(
                    mission["id"],
                    "execution_completed",
                    {"evidence_hash": evidence["output_hashes"]},
                )
                await create_governance_review(mission["id"], governance_summary)
                await create_compliance_review(mission["id"], compliance_summary)
                await create_audit_event(
                    mission["id"],
                    "assurance_scored",
                    {
                        "trust_score": trust_summary["score"],
                        "certification": trust_summary["certification"],
                        "consensus": cross_validation["consensus"],
                        "compliance_score": compliance_summary["score"],
                        "compliance_status": compliance_summary["status"],
                    },
                )
                await create_audit_event(
                    mission["id"],
                    "governance_enforced",
                    {"enforcement": enforcement.__dict__},
                )
                await record_ledger_event(
                    "mission_completed",
                    amount_cents=0,
                    currency=None,
                    mission_id=mission.get("id"),
                    metadata={
                        "certification": trust_summary["certification"],
                        "trust_score": trust_summary["score"],
                        "compliance_score": compliance_summary["score"],
                    },
                )

    return {
        "outputs": output_map,
        "evidence": evidence,
        "governance": governance_summary,
    }


async def call_gemini(prompt: str) -> str:
    if not GEMINI_KEY:
        return "Gemini Error: GEMINI_KEY not configured."
    last_error = None
    for model_name in GEMINI_MODEL_LIST:
        try:
            model = get_gemini_model(model_name)
            result = await asyncio.to_thread(model.generate_content, prompt)
            return result.text
        except Exception as exc:
            last_error = exc
            continue
    return f"Gemini Error: {last_error}"


async def call_gpt(prompt: str) -> str:
    if not openai_client:
        return "GPT Error: OPENAI_KEY not configured."
    last_error = None
    for model_name in OPENAI_MODEL_LIST:
        try:
            response = await asyncio.to_thread(
                openai_client.chat.completions.create,
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as exc:
            last_error = exc
            continue
    return f"GPT Error: {last_error}"


async def call_grok(prompt: str) -> str:
    if not xai_client:
        return "Grok Error: XAI_KEY not configured."
    last_error = None
    for model_name in XAI_MODEL_LIST:
        try:
            response = await asyncio.to_thread(
                xai_client.chat.completions.create,
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as exc:
            last_error = exc
            continue
    return f"Grok Error: {last_error}"


async def call_claude(prompt: str) -> str:
    if not anthropic_client:
        return "Claude Error: ANTHROPIC_KEY not configured."
    last_error = None
    for model_name in ANTHROPIC_MODEL_LIST:
        try:
            response = await asyncio.to_thread(
                anthropic_client.messages.create,
                model=model_name,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text if response.content else ""
            return content
        except Exception as exc:
            last_error = exc
            continue
    return f"Claude Error: {last_error}"


@app.get("/")
async def root():
    if INDEX_PATH.exists():
        return FileResponse(INDEX_PATH, media_type="text/html")
    return {"status": "ok", "detail": "index.html not found"}


@app.get("/admin")
async def admin():
    if ADMIN_PATH.exists():
        return FileResponse(ADMIN_PATH, media_type="text/html")
    return {"status": "ok", "detail": "admin.html not found"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "providers": {
            "gemini": gemini_model is not None,
            "openai": openai_client is not None,
            "xai": xai_client is not None,
            "anthropic": anthropic_client is not None,
            "supabase": supabase_client is not None,
            "stripe": bool(STRIPE_SECRET_KEY),
            "neo3": True,
            "evolution": True,
        },
    }


@app.post("/briefings")
async def create_briefing(request: BriefingRequest):
    require_supabase()
    mission = await supabase_insert(
        SUPABASE_MISSIONS_TABLE,
        {
            "status": "briefing",
            "prompt": request.prompt,
            "context": request.context,
            "metadata": {
                **(request.metadata or {}),
                "domain_id": request.domain_id,
                "domain_name": request.domain_name,
            },
        },
    )
    if not mission:
        raise HTTPException(status_code=500, detail="Failed to create mission.")
    await create_audit_event(
        mission["id"],
        "briefing_created",
        {"prompt_length": len(request.prompt)},
    )
    return {"mission_id": mission["id"], "status": mission["status"]}


@app.post("/quote")
async def create_quote(request: QuoteRequest):
    require_supabase()
    mission = await supabase_fetch_single(SUPABASE_MISSIONS_TABLE, {"id": request.mission_id})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found.")
    file_count = (mission.get("metadata") or {}).get("file_count", 0)
    quote = estimate_quote(
        mission.get("prompt", ""),
        mission.get("context"),
        file_count,
        request.complexity_override,
    )
    updated = await supabase_update(
        SUPABASE_MISSIONS_TABLE,
        {"id": request.mission_id},
        {
            "status": "quoted",
            "quote_cents": quote["total_cents"],
            "quote_currency": quote["currency"],
            "quote_breakdown": quote["breakdown"],
        },
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to store quote.")
    await create_audit_event(
        request.mission_id,
        "quote_created",
        {"quote_cents": quote["total_cents"], "currency": quote["currency"]},
    )
    return {
        "mission_id": request.mission_id,
        "quote_cents": quote["total_cents"],
        "currency": quote["currency"],
        "breakdown": quote["breakdown"],
    }


@app.post("/checkout")
async def create_checkout(request: CheckoutRequest):
    require_supabase()
    require_stripe()
    mission = await supabase_fetch_single(SUPABASE_MISSIONS_TABLE, {"id": request.mission_id})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found.")
    if not mission.get("quote_cents"):
        raise HTTPException(status_code=400, detail="Quote required before checkout.")
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=STRIPE_PAYMENT_METHOD_TYPES,
        line_items=[
            {
                "price_data": {
                    "currency": mission.get("quote_currency", STRIPE_CURRENCY),
                    "product_data": {"name": "Trinity Mission"},
                    "unit_amount": mission["quote_cents"],
                },
                "quantity": 1,
            }
        ],
        success_url=STRIPE_SUCCESS_URL,
        cancel_url=STRIPE_CANCEL_URL,
        metadata={"mission_id": request.mission_id},
    )
    await supabase_update(
        SUPABASE_MISSIONS_TABLE,
        {"id": request.mission_id},
        {
            "status": "checkout",
            "stripe_session_id": session.id,
        },
    )
    await create_audit_event(
        request.mission_id,
        "checkout_created",
        {"stripe_session_id": session.id},
    )
    return {"mission_id": request.mission_id, "checkout_url": session.url}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    require_supabase()
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe webhook secret not configured.")
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Webhook error: {exc}") from exc
    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        mission_id = session.get("metadata", {}).get("mission_id")
        if mission_id:
            await supabase_update(
                SUPABASE_MISSIONS_TABLE,
                {"id": mission_id},
                {
                    "status": "paid",
                    "stripe_payment_intent_id": session.get("payment_intent"),
                    "paid_at": utc_now_iso(),
                },
            )
            await create_audit_event(
                mission_id,
                "payment_captured",
                {"stripe_session_id": session.get("id")},
            )
            amount_total = session.get("amount_total")
            currency = session.get("currency")
            if amount_total:
                await record_ledger_event(
                    "revenue_captured",
                    amount_cents=int(amount_total),
                    currency=currency,
                    mission_id=mission_id,
                    metadata={"source": "stripe", "session_id": session.get("id")},
                )
                vault_allocation = int(amount_total * TRINITY_LEDGER_VAULT_RATE)
                if vault_allocation > 0:
                    await record_ledger_event(
                        "world_auto_vault_allocation",
                        amount_cents=vault_allocation,
                        currency=currency,
                        mission_id=mission_id,
                        metadata={"rate": TRINITY_LEDGER_VAULT_RATE},
                    )
                rebirth_allocation = int(amount_total * TRINITY_LEDGER_REBIRTH_RATE)
                if rebirth_allocation > 0:
                    await record_ledger_event(
                        "rebirth_protocol_allocation",
                        amount_cents=rebirth_allocation,
                        currency=currency,
                        mission_id=mission_id,
                        metadata={"rate": TRINITY_LEDGER_REBIRTH_RATE},
                    )
    return {"received": True}


@app.get("/missions/{mission_id}")
async def get_mission(mission_id: str):
    require_supabase()
    mission = await supabase_fetch_single(SUPABASE_MISSIONS_TABLE, {"id": mission_id})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found.")
    return mission


@app.get("/missions/{mission_id}/verify")
async def verify_mission(mission_id: str):
    require_supabase()
    mission = await supabase_fetch_single(SUPABASE_MISSIONS_TABLE, {"id": mission_id})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found.")
    return {
        "mission_id": mission_id,
        "status": mission.get("status"),
        "evidence": mission.get("evidence"),
        "governance": mission.get("governance"),
        "trust_score": (mission.get("governance") or {}).get("trust_score"),
        "certification": (mission.get("governance") or {}).get("certification"),
        "quote_cents": mission.get("quote_cents"),
        "currency": mission.get("quote_currency"),
    }


@app.get("/missions/{mission_id}/audit")
async def mission_audit(mission_id: str):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_AUDIT_TABLE)
            .select("*")
            .eq("mission_id", mission_id)
            .order("created_at")
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select)
        return {"mission_id": mission_id, "events": getattr(response, "data", [])}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit: {exc}") from exc


@app.get("/system/status")
async def system_status():
    status = {
        "providers": {
            "gemini": gemini_model is not None,
            "openai": openai_client is not None,
            "xai": xai_client is not None,
            "anthropic": anthropic_client is not None,
            "supabase": supabase_client is not None,
            "stripe": bool(STRIPE_SECRET_KEY),
            "neo3": True,
            "evolution": True,
            "ledger": supabase_client is not None,
        }
    }
    if not supabase_client:
        return status

    def _select_status():
        return (
            supabase_client.table(SUPABASE_MISSIONS_TABLE)
            .select("status")
            .execute()
        )

    try:
        response = await asyncio.to_thread(_select_status)
        data = getattr(response, "data", []) or []
        counts: Dict[str, int] = {}
        for item in data:
            value = item.get("status") or "unknown"
            counts[value] = counts.get(value, 0) + 1
        status["missions"] = counts
    except Exception as exc:
        status["missions_error"] = str(exc)
    return status


@app.get("/governance/policies")
async def list_governance_policies():
    require_supabase()

    def _select():
        return supabase_client.table(SUPABASE_GOVERNANCE_TABLE).select("*").execute()

    response = await asyncio.to_thread(_select)
    return {"policies": getattr(response, "data", [])}


@app.post("/governance/policies")
async def create_governance_policy(request: GovernancePolicyRequest):
    require_supabase()
    try:
        re.compile(request.pattern)
    except re.error as exc:
        raise HTTPException(status_code=400, detail=f"Invalid pattern: {exc}") from exc
    policy = await supabase_insert(
        SUPABASE_GOVERNANCE_TABLE,
        {
            "name": request.name,
            "pattern": request.pattern,
            "severity": request.severity,
            "scope": request.scope,
            "enabled": request.enabled,
            "metadata": request.metadata or {},
        },
    )
    if not policy:
        raise HTTPException(status_code=500, detail="Failed to create policy.")
    governance_cache["policies"] = []
    governance_cache["expires_at"] = 0.0
    return policy


@app.get("/governance/protocols")
async def list_governance_protocols():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_GOVERNANCE_PROTOCOLS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"protocols": getattr(response, "data", [])}


@app.post("/governance/protocols")
async def create_governance_protocol(request: GovernanceProtocolRequest):
    require_supabase()
    protocol = await supabase_insert(
        SUPABASE_GOVERNANCE_PROTOCOLS_TABLE,
        {
            "name": request.name,
            "cadence": request.cadence,
            "scope": request.scope,
            "description": request.description,
            "human_roles": request.human_roles or [],
            "ai_roles": request.ai_roles or [],
            "steps": request.steps or [],
            "evidence_requirements": request.evidence_requirements or {},
            "escalation": request.escalation or {},
            "metadata": request.metadata or {},
        },
    )
    if not protocol:
        raise HTTPException(status_code=500, detail="Failed to create protocol.")
    return protocol


@app.get("/connectors")
async def list_connectors():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_CONNECTORS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"connectors": getattr(response, "data", [])}


@app.post("/connectors")
async def create_connector(request: ConnectorRequest):
    require_supabase()
    connector = await supabase_insert(
        SUPABASE_CONNECTORS_TABLE,
        {
            "name": request.name,
            "connector_type": request.connector_type,
            "description": request.description,
            "status": request.status,
            "edge_url": request.edge_url,
            "scopes": request.scopes or [],
            "config": request.config or {},
            "metadata": request.metadata or {},
        },
    )
    if not connector:
        raise HTTPException(status_code=500, detail="Failed to create connector.")
    return connector


@app.get("/connectors/{connector_id}")
async def get_connector(connector_id: str):
    require_supabase()
    connector = await supabase_fetch_single(SUPABASE_CONNECTORS_TABLE, {"id": connector_id})
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found.")
    return connector


@app.patch("/connectors/{connector_id}")
async def update_connector(connector_id: str, request: ConnectorUpdateRequest):
    require_supabase()
    payload = request.dict(exclude_unset=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No updates provided.")
    connector = await supabase_update(
        SUPABASE_CONNECTORS_TABLE,
        {"id": connector_id},
        payload,
    )
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found.")
    return connector


@app.get("/connectors/{connector_id}/runs")
async def list_connector_runs(connector_id: str, limit: int = 50):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_CONNECTOR_RUNS_TABLE)
            .select("*")
            .eq("connector_id", connector_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"runs": getattr(response, "data", [])}


@app.post("/connectors/{connector_id}/invoke")
async def invoke_connector(connector_id: str, request: ConnectorInvokeRequest):
    require_supabase()
    connector = await supabase_fetch_single(SUPABASE_CONNECTORS_TABLE, {"id": connector_id})
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found.")
    if (connector.get("status") or "").lower() not in {"active", "enabled"}:
        raise HTTPException(status_code=400, detail="Connector is not active.")
    edge_url = connector.get("edge_url")
    if not edge_url:
        raise HTTPException(status_code=400, detail="Connector missing edge_url.")
    if not is_allowed_edge_url(edge_url):
        raise HTTPException(status_code=403, detail="Connector edge_url not allowed.")

    method = (request.method or "POST").upper()
    if method not in {"POST", "GET"}:
        raise HTTPException(status_code=400, detail="Only GET and POST are supported.")
    target_url = build_edge_url(edge_url, request.path, request.query)
    headers = request.headers or {}
    payload = request.payload or {}
    data = None
    if method == "POST":
        data = json.dumps(payload).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    def _invoke():
        req = urllib_request.Request(target_url, data=data, headers=headers, method=method)
        try:
            with urllib_request.urlopen(req, timeout=request.timeout or TRINITY_CONNECTOR_TIMEOUT) as resp:
                return {"status": resp.status, "body": resp.read(), "error": None}
        except urllib_error.HTTPError as exc:
            body = exc.read() if exc.fp else b""
            return {"status": exc.code, "body": body, "error": str(exc)}
        except Exception as exc:
            return {"status": 0, "body": b"", "error": str(exc)}

    result = await asyncio.to_thread(_invoke)
    response_text = result["body"].decode("utf-8", errors="replace")
    try:
        response_payload = json.loads(response_text) if response_text else {}
    except json.JSONDecodeError:
        response_payload = {"raw": response_text}
    response_payload = truncate_payload(response_payload)
    status = "success" if 200 <= result["status"] < 300 else "failed"
    if result["status"] == 0:
        status = "error"

    run = await supabase_insert(
        SUPABASE_CONNECTOR_RUNS_TABLE,
        {
            "connector_id": connector_id,
            "status": status,
            "request_payload": request.payload or {},
            "response_payload": response_payload,
            "response_status": result["status"],
            "error": result["error"],
            "metadata": request.metadata or {},
        },
    )
    if not run:
        raise HTTPException(status_code=500, detail="Failed to record connector run.")
    return {"connector": connector, "run": run, "response": response_payload}


@app.post("/governance/review")
async def governance_review(request: GovernanceReviewRequest):
    require_supabase()
    mission = await supabase_fetch_single(SUPABASE_MISSIONS_TABLE, {"id": request.mission_id})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found.")
    outputs = {
        "gemini": mission.get("gemini", ""),
        "gpt": mission.get("gpt", ""),
        "grok": mission.get("grok", ""),
        "claude": mission.get("claude", ""),
    }
    policies = await get_governance_policies()
    summary = evaluate_governance(outputs, policies)
    new_status = "completed" if summary["status"] == "pass" else "review"
    await supabase_update(
        SUPABASE_MISSIONS_TABLE,
        {"id": request.mission_id},
        {"governance": summary, "status": new_status},
    )
    await create_governance_review(request.mission_id, summary)
    await create_audit_event(
        request.mission_id, "governance_review", {"status": summary["status"]}
    )
    return {"mission_id": request.mission_id, "governance": summary}


@app.post("/missions/{mission_id}/retry")
async def retry_mission(mission_id: str):
    require_supabase()
    mission = await supabase_fetch_single(SUPABASE_MISSIONS_TABLE, {"id": mission_id})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found.")
    if mission.get("status") not in {"review", "failed", "completed"}:
        raise HTTPException(status_code=400, detail="Mission not eligible for retry.")
    prompt = mission.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Mission missing prompt.")
    file_context = mission.get("file_context", "") or ""
    file_names = mission.get("file_names") or []
    file_hashes = (mission.get("evidence") or {}).get("file_hashes", {}) or {}
    execution = await run_execution(
        prompt,
        file_context,
        file_names,
        file_hashes,
        mission_id=mission_id,
        run_reason="retry",
    )
    return {
        "mission_id": mission_id,
        "outputs": execution["outputs"],
        "governance": execution["governance"],
    }


@app.get("/evolution/proposals")
async def list_evolution_proposals():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_EVOLUTION_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"proposals": getattr(response, "data", [])}


@app.post("/evolution/proposals")
async def create_evolution_proposal(request: EvolutionProposalRequest):
    require_supabase()
    proposal = await supabase_insert(
        SUPABASE_EVOLUTION_TABLE,
        {
            "title": request.title,
            "description": request.description,
            "rationale": request.rationale,
            "payload": request.payload or {},
            "status": "pending",
        },
    )
    if not proposal:
        raise HTTPException(status_code=500, detail="Failed to create proposal.")
    return proposal


@app.post("/evolution/proposals/{proposal_id}/approve")
async def approve_evolution_proposal(proposal_id: str):
    require_supabase()
    proposal = await supabase_update(
        SUPABASE_EVOLUTION_TABLE,
        {"id": proposal_id},
        {"status": "approved", "approved_at": utc_now_iso()},
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal


@app.get("/evolution/playbooks")
async def list_evolution_playbooks():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_EVOLUTION_PLAYBOOKS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"playbooks": getattr(response, "data", [])}


@app.post("/evolution/playbooks")
async def create_evolution_playbook(request: EvolutionPlaybookRequest):
    require_supabase()
    playbook = await supabase_insert(
        SUPABASE_EVOLUTION_PLAYBOOKS_TABLE,
        {
            "name": request.name,
            "description": request.description,
            "stages": request.stages or [],
            "guardrails": request.guardrails or {},
            "required_metrics": request.required_metrics or {},
            "approval_chain": request.approval_chain or [],
            "metadata": request.metadata or {},
        },
    )
    if not playbook:
        raise HTTPException(status_code=500, detail="Failed to create playbook.")
    return playbook


@app.get("/academy/modules")
async def list_academy_modules():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_ACADEMY_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"modules": getattr(response, "data", [])}


@app.post("/academy/modules")
async def create_academy_module(request: AcademyModuleRequest):
    require_supabase()
    module = await supabase_insert(
        SUPABASE_ACADEMY_TABLE,
        {
            "title": request.title,
            "summary": request.summary,
            "level": request.level,
            "status": request.status,
            "content": request.content or {},
            "tags": request.tags or [],
            "metadata": request.metadata or {},
        },
    )
    if not module:
        raise HTTPException(status_code=500, detail="Failed to create module.")
    return module


@app.get("/deployments")
async def list_deployments():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_DEPLOYMENTS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"deployments": getattr(response, "data", [])}


@app.post("/deployments")
async def create_deployment(request: DeploymentRequest):
    require_supabase()
    deployment = await supabase_insert(
        SUPABASE_DEPLOYMENTS_TABLE,
        {
            "version": request.version,
            "environment": request.environment,
            "status": request.status,
            "artifacts": request.artifacts or {},
            "notes": request.notes,
        },
    )
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to create deployment.")
    return deployment


@app.get("/agents/tiers")
async def list_agent_tiers():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_AGENT_TIERS_TABLE)
            .select("*")
            .order("tier_level")
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"tiers": getattr(response, "data", [])}


@app.post("/agents/tiers")
async def create_agent_tier(request: AgentTierRequest):
    require_supabase()
    tier = await supabase_insert(
        SUPABASE_AGENT_TIERS_TABLE,
        {
            "name": request.name,
            "tier_level": request.tier_level,
            "description": request.description,
            "min_usd": request.min_usd,
            "max_usd": request.max_usd,
            "required_certifications": request.required_certifications or [],
            "required_badges": request.required_badges or [],
            "autonomy_level": request.autonomy_level,
            "allowed_domains": request.allowed_domains or [],
            "review_requirements": request.review_requirements or {},
            "metadata": request.metadata or {},
        },
    )
    if not tier:
        raise HTTPException(status_code=500, detail="Failed to create agent tier.")
    return tier


@app.get("/bots/task-tiers")
async def list_bot_task_tiers():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_BOT_TASK_TIERS_TABLE)
            .select("*")
            .order("tier_level")
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"tiers": getattr(response, "data", [])}


@app.post("/bots/task-tiers")
async def create_bot_task_tier(request: BotTaskTierRequest):
    require_supabase()
    tier = await supabase_insert(
        SUPABASE_BOT_TASK_TIERS_TABLE,
        {
            "name": request.name,
            "tier_level": request.tier_level,
            "description": request.description,
            "min_usd": request.min_usd,
            "max_usd": request.max_usd,
            "allowed_sources": request.allowed_sources or [],
            "task_types": request.task_types or [],
            "risk_controls": request.risk_controls or [],
            "evidence_requirements": request.evidence_requirements or [],
            "metadata": request.metadata or {},
        },
    )
    if not tier:
        raise HTTPException(status_code=500, detail="Failed to create bot task tier.")
    return tier


@app.get("/domains")
async def list_domains(name: Optional[str] = None):
    require_supabase()

    def _select():
        query = supabase_client.table(SUPABASE_DOMAIN_TABLE).select("*")
        if name:
            query = query.eq("name", name)
        return query.order("created_at", desc=True).execute()

    response = await asyncio.to_thread(_select)
    return {"domains": getattr(response, "data", [])}


@app.post("/domains")
async def create_domain(request: DomainProfileRequest):
    require_supabase()
    profile = await supabase_insert(
        SUPABASE_DOMAIN_TABLE,
        {
            "name": request.name,
            "description": request.description,
            "compliance_threshold": request.compliance_threshold,
            "trust_threshold": request.trust_threshold,
            "consensus_threshold": request.consensus_threshold,
            "required_certifications": request.required_certifications or [],
            "policy_tags": request.policy_tags or [],
            "metadata": request.metadata or {},
        },
    )
    if not profile:
        raise HTTPException(status_code=500, detail="Failed to create domain.")
    return profile


@app.get("/domains/{domain_id}")
async def get_domain(domain_id: str):
    require_supabase()
    domain = await supabase_fetch_single(SUPABASE_DOMAIN_TABLE, {"id": domain_id})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found.")
    return domain


@app.get("/domains/{domain_id}/certifications")
async def list_domain_certifications(domain_id: str):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_DOMAIN_CERT_TABLE)
            .select("*")
            .eq("domain_id", domain_id)
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"certifications": getattr(response, "data", [])}


@app.post("/domains/{domain_id}/certifications")
async def create_domain_certification(domain_id: str, request: DomainCertificationRequest):
    require_supabase()
    certification = await supabase_insert(
        SUPABASE_DOMAIN_CERT_TABLE,
        {
            "domain_id": domain_id,
            "agent_name": request.agent_name,
            "certification_level": request.certification_level,
            "valid_from": request.valid_from,
            "valid_to": request.valid_to,
            "evidence": request.evidence or {},
            "metadata": request.metadata or {},
        },
    )
    if not certification:
        raise HTTPException(status_code=500, detail="Failed to create certification.")
    return certification


@app.get("/domains/{domain_id}/badges")
async def list_domain_badges(domain_id: str):
    require_supabase()
    badges = await fetch_domain_badges(domain_id)
    return {"badges": badges}


@app.post("/domains/{domain_id}/badges")
async def create_domain_badge(domain_id: str, request: DomainBadgeRequest):
    require_supabase()
    badge = await supabase_insert(
        SUPABASE_DOMAIN_BADGE_TABLE,
        {
            "domain_id": domain_id,
            "name": request.name,
            "description": request.description,
            "level": request.level,
            "criteria": request.criteria or {},
            "metadata": request.metadata or {},
        },
    )
    if not badge:
        raise HTTPException(status_code=500, detail="Failed to create badge.")
    return badge


@app.get("/domains/{domain_id}/compliance-templates")
async def list_domain_compliance_templates(domain_id: str):
    require_supabase()
    templates = await fetch_domain_templates(domain_id)
    return {"templates": templates}


@app.post("/domains/{domain_id}/compliance-templates")
async def create_domain_compliance_template(domain_id: str, request: ComplianceTemplateRequest):
    require_supabase()
    template = await supabase_insert(
        SUPABASE_COMPLIANCE_TEMPLATE_TABLE,
        {
            "domain_id": domain_id,
            "name": request.name,
            "validator_instructions": request.validator_instructions,
            "policy_rules": request.policy_rules or [],
            "severity": request.severity,
            "tags": request.tags or [],
            "metadata": request.metadata or {},
        },
    )
    if not template:
        raise HTTPException(status_code=500, detail="Failed to create compliance template.")
    return template


@app.get("/domains/{domain_id}/exams")
async def list_certification_exams(domain_id: str):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_CERT_EXAM_TABLE)
            .select("*")
            .eq("domain_id", domain_id)
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"exams": getattr(response, "data", [])}


@app.post("/domains/{domain_id}/exams")
async def create_certification_exam(domain_id: str, request: CertificationExamRequest):
    require_supabase()
    exam = await supabase_insert(
        SUPABASE_CERT_EXAM_TABLE,
        {
            "domain_id": domain_id,
            "title": request.title,
            "description": request.description,
            "pass_score": request.pass_score,
            "certification_level": request.certification_level,
            "rubric": request.rubric or {},
            "questions": request.questions or [],
            "metadata": request.metadata or {},
        },
    )
    if not exam:
        raise HTTPException(status_code=500, detail="Failed to create exam.")
    return exam


@app.post("/domains/{domain_id}/exams/{exam_id}/submit")
async def submit_certification_exam(
    domain_id: str,
    exam_id: str,
    request: CertificationExamSubmissionRequest,
):
    require_supabase()
    exam = await supabase_fetch_single(SUPABASE_CERT_EXAM_TABLE, {"id": exam_id})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")
    score = request.score
    pass_score = int(exam.get("pass_score", 85))
    status = "pass" if score >= pass_score else "fail"
    result = await supabase_insert(
        SUPABASE_CERT_EXAM_RESULTS_TABLE,
        {
            "domain_id": domain_id,
            "exam_id": exam_id,
            "agent_name": request.agent_name,
            "score": score,
            "status": status,
            "details": request.details or {},
        },
    )
    if status == "pass":
        await supabase_insert(
            SUPABASE_DOMAIN_CERT_TABLE,
            {
                "domain_id": domain_id,
                "agent_name": request.agent_name,
                "certification_level": exam.get("certification_level") or "certified",
                "valid_from": utc_now_iso(),
                "valid_to": None,
                "evidence": {
                    "exam_id": exam_id,
                    "score": score,
                    "pass_score": pass_score,
                },
                "metadata": {},
            },
        )
    return {"status": status, "result": result}


@app.get("/board/members")
async def list_board_members():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_BOARD_MEMBERS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"members": getattr(response, "data", [])}


@app.post("/board/members")
async def create_board_member(request: BoardMemberRequest):
    require_supabase()
    member = await supabase_insert(
        SUPABASE_BOARD_MEMBERS_TABLE,
        {
            "name": request.name,
            "member_type": request.member_type,
            "role": request.role,
            "active": request.active,
            "metadata": request.metadata or {},
        },
    )
    if not member:
        raise HTTPException(status_code=500, detail="Failed to create member.")
    return member


@app.get("/board/terms")
async def list_board_terms():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_BOARD_TERMS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"terms": getattr(response, "data", [])}


@app.post("/board/terms")
async def create_board_term(request: BoardTermRequest):
    require_supabase()
    term = await supabase_insert(
        SUPABASE_BOARD_TERMS_TABLE,
        {
            "term_label": request.term_label,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "status": request.status,
            "metadata": request.metadata or {},
        },
    )
    if not term:
        raise HTTPException(status_code=500, detail="Failed to create term.")
    return term


@app.get("/board/terms/{term_id}/assignments")
async def list_board_assignments(term_id: str):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_BOARD_ASSIGNMENTS_TABLE)
            .select("*")
            .eq("term_id", term_id)
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"assignments": getattr(response, "data", [])}


@app.post("/board/terms/{term_id}/assignments")
async def create_board_assignment(term_id: str, request: BoardAssignmentRequest):
    require_supabase()
    assignment = await supabase_insert(
        SUPABASE_BOARD_ASSIGNMENTS_TABLE,
        {
            "term_id": term_id,
            "member_id": request.member_id,
            "seat": request.seat,
            "responsibility": request.responsibility,
            "active": request.active,
            "metadata": request.metadata or {},
        },
    )
    if not assignment:
        raise HTTPException(status_code=500, detail="Failed to create assignment.")
    return assignment


@app.get("/board/criteria")
async def list_board_criteria():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_BOARD_CRITERIA_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"criteria": getattr(response, "data", [])}


@app.post("/board/criteria")
async def create_board_criteria(request: BoardCriteriaRequest):
    require_supabase()
    criteria = await supabase_insert(
        SUPABASE_BOARD_CRITERIA_TABLE,
        {
            "name": request.name,
            "description": request.description,
            "category": request.category,
            "weight_default": request.weight_default,
            "is_active": request.is_active,
            "metadata": request.metadata or {},
        },
    )
    if not criteria:
        raise HTTPException(status_code=500, detail="Failed to create criteria.")
    return criteria


@app.post("/board/sessions")
async def create_board_session(request: BoardSessionRequest):
    require_supabase()
    require_board_secret()
    criteria = await fetch_active_board_criteria()
    if not criteria:
        raise HTTPException(status_code=400, detail="No active board criteria.")
    session_id = str(uuid.uuid4())
    payload = build_board_criteria_payload(
        criteria,
        seed=session_id,
        count=TRINITY_BOARD_CRITERIA_COUNT,
    )
    commit = build_board_commit(payload)
    session = await supabase_insert(
        SUPABASE_BOARD_SESSIONS_TABLE,
        {
            "id": session_id,
            "term_id": request.term_id,
            "mission_id": request.mission_id,
            "domain_id": request.domain_id,
            "title": request.title,
            "criteria_commit": commit,
            "criteria_payload": None,
            "metadata": request.metadata or {},
        },
    )
    if not session:
        raise HTTPException(status_code=500, detail="Failed to create session.")
    return {"session_id": session_id, "criteria_commit": commit}


@app.get("/board/sessions/{session_id}")
async def get_board_session(session_id: str):
    require_supabase()
    session = await supabase_fetch_single(SUPABASE_BOARD_SESSIONS_TABLE, {"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if not session.get("revealed_at"):
        session["criteria_payload"] = None
    return session


@app.post("/board/sessions/{session_id}/reveal")
async def reveal_board_session(session_id: str):
    require_supabase()
    require_board_secret()
    session = await supabase_fetch_single(SUPABASE_BOARD_SESSIONS_TABLE, {"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.get("revealed_at"):
        return session
    criteria = await fetch_active_board_criteria()
    payload = build_board_criteria_payload(
        criteria,
        seed=session_id,
        count=TRINITY_BOARD_CRITERIA_COUNT,
    )
    commit = build_board_commit(payload)
    if commit != session.get("criteria_commit"):
        raise HTTPException(status_code=400, detail="Criteria commit mismatch.")
    updated = await supabase_update(
        SUPABASE_BOARD_SESSIONS_TABLE,
        {"id": session_id},
        {"criteria_payload": payload, "revealed_at": utc_now_iso()},
    )
    return updated or session


@app.get("/board/sessions/{session_id}/scores")
async def list_board_scores(session_id: str):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_BOARD_SCORES_TABLE)
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"scores": getattr(response, "data", [])}


@app.post("/board/sessions/{session_id}/scores")
async def create_board_score(session_id: str, request: BoardScoreRequest):
    require_supabase()
    session = await supabase_fetch_single(SUPABASE_BOARD_SESSIONS_TABLE, {"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if not session.get("revealed_at"):
        raise HTTPException(status_code=400, detail="Criteria not revealed yet.")
    score = await supabase_insert(
        SUPABASE_BOARD_SCORES_TABLE,
        {
            "session_id": session_id,
            "member_id": request.member_id,
            "score": request.score,
            "notes": request.notes,
            "criteria_scores": request.criteria_scores or {},
            "metadata": request.metadata or {},
        },
    )
    if not score:
        raise HTTPException(status_code=500, detail="Failed to create score.")
    return score


@app.get("/ledger/events")
async def list_ledger_events(limit: int = 100):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_LEDGER_EVENTS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"events": getattr(response, "data", [])}


@app.post("/ledger/events")
async def create_ledger_event(request: LedgerEventRequest):
    require_supabase()
    event = await record_ledger_event(
        request.event_type,
        amount_cents=request.amount_cents or 0,
        currency=request.currency,
        mission_id=request.mission_id,
        metadata=request.metadata,
    )
    if not event:
        raise HTTPException(status_code=500, detail="Failed to create ledger event.")
    return event


@app.get("/ledger/summary")
async def ledger_summary():
    require_supabase()

    def _select():
        return supabase_client.table(SUPABASE_LEDGER_EVENTS_TABLE).select("*").execute()

    response = await asyncio.to_thread(_select)
    events = getattr(response, "data", []) or []
    totals: Dict[str, int] = {}
    for event in events:
        key = event.get("event_type") or "unknown"
        totals[key] = totals.get(key, 0) + int(event.get("amount_cents") or 0)
    return {"totals": totals, "count": len(events)}


@app.get("/ledger/anchors")
async def list_ledger_anchors():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_LEDGER_ANCHORS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"anchors": getattr(response, "data", [])}


@app.post("/ledger/anchor")
async def create_ledger_anchor(request: LedgerAnchorRequest):
    require_supabase()

    def _select_events():
        query = supabase_client.table(SUPABASE_LEDGER_EVENTS_TABLE).select("*")
        if request.period_start:
            query = query.gte("created_at", request.period_start)
        if request.period_end:
            query = query.lte("created_at", request.period_end)
        return query.execute()

    response = await asyncio.to_thread(_select_events)
    events = getattr(response, "data", []) or []
    events_payload = json.dumps(events, sort_keys=True, separators=(",", ":"))
    ledger_hash = hash_text(events_payload)
    anchor = await supabase_insert(
        SUPABASE_LEDGER_ANCHORS_TABLE,
        {
            "period_start": request.period_start,
            "period_end": request.period_end,
            "ledger_hash": ledger_hash,
            "status": "pending",
            "metadata": {
                "events_count": len(events),
                "network": TRINITY_BLOCKCHAIN_NETWORK,
                "anchor_address": TRINITY_BLOCKCHAIN_ANCHOR_ADDRESS,
            },
        },
    )
    if not anchor:
        raise HTTPException(status_code=500, detail="Failed to create anchor.")
    return anchor


@app.post("/ledger/anchors/{anchor_id}/finalize")
async def finalize_ledger_anchor(anchor_id: str, request: LedgerAnchorFinalizeRequest):
    require_supabase()
    anchor = await supabase_update(
        SUPABASE_LEDGER_ANCHORS_TABLE,
        {"id": anchor_id},
        {"tx_hash": request.tx_hash, "status": "anchored", "metadata": request.metadata or {}},
    )
    if not anchor:
        raise HTTPException(status_code=404, detail="Anchor not found.")
    return anchor


@app.get("/audits/monthly")
async def list_monthly_audits(limit: int = 50):
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_MONTHLY_AUDITS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"audits": getattr(response, "data", [])}


@app.get("/audits/events")
async def list_audit_events(limit: int = 200):
    require_supabase()
    events = await fetch_table_rows(SUPABASE_AUDIT_TABLE, limit)
    return {"events": events}


@app.post("/audits/monthly")
async def create_monthly_audit(request: MonthlyAuditRequest):
    require_supabase()
    audit = await supabase_insert(
        SUPABASE_MONTHLY_AUDITS_TABLE,
        {
            "month_label": request.month_label,
            "summary": request.summary or {},
            "metadata": request.metadata or {},
        },
    )
    if not audit:
        raise HTTPException(status_code=500, detail="Failed to create audit.")
    return audit


@app.get("/uploads")
async def list_uploads(limit: int = 50):
    require_supabase()
    uploads = await fetch_table_rows(SUPABASE_UPLOADS_TABLE, limit)
    return {"uploads": uploads}


@app.post("/uploads")
async def create_upload(file: UploadFile = File(...), metadata: Optional[str] = Form(default=None)):
    require_supabase()
    meta_payload = {}
    if metadata:
        try:
            meta_payload = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON.") from exc

    upload_id, file_path, size, digest = await save_upload(file)
    upload = await supabase_insert(
        SUPABASE_UPLOADS_TABLE,
        {
            "id": upload_id,
            "file_name": file.filename,
            "file_path": str(file_path),
            "file_size": size,
            "mime_type": file.content_type,
            "sha256": digest,
            "metadata": meta_payload,
        },
    )
    if not upload:
        raise HTTPException(status_code=500, detail="Failed to store upload metadata.")
    return upload


@app.get("/uploads/{upload_id}")
async def get_upload(upload_id: str):
    require_supabase()
    upload = await supabase_fetch_single(SUPABASE_UPLOADS_TABLE, {"id": upload_id})
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found.")
    return upload


@app.get("/uploads/{upload_id}/download")
async def download_upload(upload_id: str):
    require_supabase()
    upload = await supabase_fetch_single(SUPABASE_UPLOADS_TABLE, {"id": upload_id})
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found.")
    file_path = upload.get("file_path")
    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")
    return FileResponse(path=file_path, filename=upload.get("file_name") or Path(file_path).name)


@app.get("/exports/missions.csv")
async def export_missions_csv(limit: int = 1000):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_MISSIONS_TABLE, limit)
    return build_csv_response("missions.csv", rows)


@app.get("/exports/missions.pdf")
async def export_missions_pdf(limit: int = 500):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_MISSIONS_TABLE, limit)
    return build_pdf_response("missions.pdf", "Mission Export", rows)


@app.get("/exports/ledger.csv")
async def export_ledger_csv(limit: int = 1000):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_LEDGER_EVENTS_TABLE, limit)
    return build_csv_response("ledger.csv", rows)


@app.get("/exports/ledger.pdf")
async def export_ledger_pdf(limit: int = 500):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_LEDGER_EVENTS_TABLE, limit)
    return build_pdf_response("ledger.pdf", "Ledger Export", rows)


@app.get("/exports/audits.csv")
async def export_audits_csv(limit: int = 1000):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_AUDIT_TABLE, limit)
    return build_csv_response("audits.csv", rows)


@app.get("/exports/audits.pdf")
async def export_audits_pdf(limit: int = 500):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_AUDIT_TABLE, limit)
    return build_pdf_response("audits.pdf", "Audit Events Export", rows)


@app.get("/exports/monthly-audits.csv")
async def export_monthly_audits_csv(limit: int = 200):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_MONTHLY_AUDITS_TABLE, limit)
    return build_csv_response("monthly_audits.csv", rows)


@app.get("/exports/monthly-audits.pdf")
async def export_monthly_audits_pdf(limit: int = 200):
    require_supabase()
    rows = await fetch_table_rows(SUPABASE_MONTHLY_AUDITS_TABLE, limit)
    return build_pdf_response("monthly_audits.pdf", "Monthly Audits Export", rows)


@app.get("/packages")
async def list_packages():
    require_supabase()

    def _select():
        return (
            supabase_client.table(SUPABASE_PACKAGE_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    response = await asyncio.to_thread(_select)
    return {"packages": getattr(response, "data", [])}


@app.post("/packages")
async def create_package(request: KnowledgePackageRequest):
    require_supabase()
    content_hash = hash_text(request.content) if request.content else None
    package = await supabase_insert(
        SUPABASE_PACKAGE_TABLE,
        {
            "name": request.name,
            "description": request.description,
            "category": request.category,
            "source": request.source,
            "url": request.url,
            "summary": request.summary,
            "content_hash": content_hash,
            "tags": request.tags or [],
            "metadata": request.metadata or {},
        },
    )
    if not package:
        raise HTTPException(status_code=500, detail="Failed to create package.")
    return package


@app.get("/domains/{domain_id}/packages")
async def list_domain_packages(domain_id: str):
    require_supabase()
    packages = await fetch_domain_packages(domain_id)
    return {"packages": packages}


@app.post("/domains/{domain_id}/packages")
async def link_domain_package(domain_id: str, request: DomainPackageLinkRequest):
    require_supabase()
    package = await supabase_fetch_single(SUPABASE_PACKAGE_TABLE, {"id": request.package_id})
    if not package:
        raise HTTPException(status_code=404, detail="Package not found.")
    link = await supabase_insert(
        SUPABASE_DOMAIN_PACKAGE_TABLE,
        {
            "domain_id": domain_id,
            "package_id": request.package_id,
            "package_name": package.get("name"),
            "role": request.role,
            "priority": request.priority,
            "metadata": request.metadata or {},
        },
    )
    if not link:
        raise HTTPException(status_code=500, detail="Failed to link package.")
    return link


@app.get("/domains/{domain_id}/documents")
async def list_domain_documents(domain_id: str, limit: int = TRINITY_DOCS_LIMIT):
    require_supabase()
    documents = await fetch_domain_documents(domain_id, limit)
    return {"documents": documents}


@app.get("/documents/{document_id}/taxonomy")
async def list_document_taxonomy(document_id: str, limit: int = 50):
    require_supabase()
    taxonomy = await fetch_document_taxonomy(document_id, limit)
    return {"taxonomy": taxonomy}


@app.get("/evolution/status")
async def evolution_status():
    engine = get_self_improvement_engine()
    status = engine.get_status()
    signature = sign_payload(status)
    return {"status": status, "signature": signature}


@app.post("/evolution/run")
async def run_evolution(request: EvolutionRunRequest):
    engine = get_self_improvement_engine()
    result = await asyncio.to_thread(engine.improve, request.iterations)
    status = engine.get_status()
    payload = {"result": result, "status": status}
    signature = sign_payload(payload)

    if supabase_client:
        await record_evolution_run(
            {
                "iterations": request.iterations,
                "result": result,
                "status": status,
                "signature": signature,
            }
        )
    return {"result": result, "status": status, "signature": signature}


@app.get("/neo3/status")
async def neo3_status():
    system = get_neo3_system()
    status = system.get_status()
    signature = sign_payload(status)
    return {"status": status, "signature": signature}


@app.post("/neo3/process")
async def neo3_process(request: Neo3ProcessRequest):
    system = get_neo3_system()
    result = await asyncio.to_thread(system.process, request.input_data)
    signature = sign_payload(result)
    return {"result": result, "signature": signature}


@app.post("/neo3/train")
async def neo3_train(request: Neo3TrainRequest):
    system = get_neo3_system()
    if not request.training_data:
        raise HTTPException(status_code=400, detail="Training data is required.")
    if len(request.training_data) > 50:
        raise HTTPException(status_code=400, detail="Training data exceeds 50 items.")
    result = await asyncio.to_thread(system.train, request.training_data)
    signature = sign_payload(result)
    return {"result": result, "signature": signature}


@app.post("/neo3/evolve")
async def neo3_evolve(request: Neo3EvolveRequest):
    system = get_neo3_system()
    await asyncio.to_thread(system.evolve, request.iterations)
    status = system.get_status()
    signature = sign_payload(status)
    return {"status": status, "signature": signature}


@app.post("/execute")
async def execute_mission(
    prompt: Optional[str] = Form(default=None),
    files: Optional[List[UploadFile]] = File(default=None),
    mission_id: Optional[str] = Form(default=None),
    domain_id: Optional[str] = Form(default=None),
    domain_name: Optional[str] = Form(default=None),
):
    file_context = ""
    file_names: List[str] = []
    file_hashes: Dict[str, str] = {}
    if files:
        for file in files:
            content = await file.read()
            if not content:
                continue
            file_names.append(file.filename)
            file_hashes[file.filename] = hash_bytes(content)
            try:
                text = content.decode("utf-8")
                file_context += f"\n--- FILE: {file.filename} ---\n{text}\n"
            except UnicodeDecodeError:
                file_context += f"\n--- FILE: {file.filename} (Binary) ---\n"

    mission = None
    if mission_id:
        require_supabase()
        mission = await supabase_fetch_single(SUPABASE_MISSIONS_TABLE, {"id": mission_id})
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found.")
        if mission.get("status") not in {"paid", "executing"}:
            raise HTTPException(status_code=400, detail="Mission not approved for execution.")
        if not prompt:
            prompt = mission.get("prompt")
        if not file_context:
            file_context = mission.get("file_context", "") or ""

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")

    execution = await run_execution(
        prompt,
        file_context,
        file_names,
        file_hashes,
        mission_id=mission_id,
        domain_id=domain_id,
        domain_name=domain_name,
        run_reason="api",
    )
    # UI consumption boundary:
    # - execution_id, industry, severity, allow/block are in execution["governance"]["enforcement"].
    # - UI may observe, never control enforcement.
    return execution["outputs"]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

