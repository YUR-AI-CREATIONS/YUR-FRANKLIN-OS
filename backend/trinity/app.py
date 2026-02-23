"""
Trinity 9.1 – Project Workspace Edition
---------------------------------------
Multi-project memory, per-project chat, full file explorer actions.
Run:
    uvicorn app:app --port 8080
Open:
    http://127.0.0.1:8080
"""
import os, json, time, shutil, traceback, datetime, asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
import uuid
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import fitz, pytesseract

from trinity_orchestrator_unified import trinity_engine as unified_trinity_engine
from config import get_config
from orchestration.scheduler import TrinityWorkloadOrchestrator

# Optional SDK imports for fallback-only paths
try:
    from openai import OpenAI
except Exception:
    OpenAI = None
try:
    from google import genai
except Exception:
    genai = None
try:
    import anthropic
except Exception:
    anthropic = None

# ───────────── API Clients (lazy) ─────────────
def _openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not (OpenAI and key):
        raise RuntimeError("OpenAI unavailable (package or OPENAI_API_KEY missing)")
    return OpenAI(api_key=key)

def _gemini_client():
    key = os.getenv("GEMINI_API_KEY")
    if not (genai and key):
        raise RuntimeError("Gemini unavailable (package or GEMINI_API_KEY missing)")
    return genai.Client(api_key=key)

def _anthropic_client():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not (anthropic and key):
        raise RuntimeError("Anthropic unavailable (package or ANTHROPIC_API_KEY missing)")
    return anthropic.Anthropic(api_key=key)

# ───────────── FastAPI ─────────────
# Import middleware
from middleware.security import SecurityHeadersMiddleware
from middleware.logging import RequestLoggingMiddleware
from middleware.errors import validation_exception_handler, http_exception_handler, general_exception_handler
from middleware.validation import validate_files, check_file_size
from middleware.tasks import task_queue
from middleware.websocket import ws_manager
from middleware.redis_client import redis_client
from fastapi import APIRouter
from routers.v1 import router as v1_router

app = FastAPI(
    title="Trinity Intelligence Console",
    version="1.0.0",
    description="Multi-project AI orchestration with Gemini, OpenAI, and Anthropic",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Mount routers
app.include_router(v1_router)

# Routers
ops_router = APIRouter(prefix="/ops")

@ops_router.get("/stats3")
def ops_stats3():
    return {
        "system": "ok",
        "projects_count": len([p for p in BASE_DIR.iterdir() if p.is_dir()]),
    }

@ops_router.get("/stats")
def ops_stats_full():
    import psutil
    return {
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        },
        "projects": {
            "total": len([p for p in BASE_DIR.iterdir() if p.is_dir()]),
        },
        "engines": get_config().missing_keys(),
    }

@ops_router.get("/logs/requests")
def ops_logs_requests(limit: int = 100):
    from middleware.logging import REQUEST_LOG
    if not REQUEST_LOG.exists():
        return {"logs": []}
    lines = REQUEST_LOG.read_text(encoding="utf-8").strip().split("\n")
    logs = [json.loads(line) for line in lines[-limit:] if line]
    return {"logs": logs, "count": len(logs)}

@ops_router.get("/logs/telemetry")
def ops_logs_telemetry(limit: int = 100):
    from telemetry import LOG_PATH
    if not LOG_PATH.exists():
        return {"logs": []}
    lines = LOG_PATH.read_text(encoding="utf-8").strip().split("\n")
    logs = [json.loads(line) for line in lines[-limit:] if line]
    return {"logs": logs, "count": len(logs)}

@ops_router.post("/delete_project2")
def ops_delete_project2(project: str = Form(...)):
    proj = BASE_DIR / project
    if not proj.exists():
        return {"error": "Project not found"}
    import shutil
    shutil.rmtree(proj)
    return {"deleted": project}

@ops_router.post("/tasks/{project}/scan")
async def ops_tasks_scan(project: str, background_tasks: BackgroundTasks):
    return await start_scan_task(project, background_tasks)

@ops_router.get("/tasks/{task_id}")
def ops_tasks_status(task_id: str):
    return get_task_status_endpoint(task_id)

app.include_router(ops_router)

# Lightweight v1 probe
@app.get("/api/v1/ping")
def v1_ping():
    return {"ok": True, "version": "v1"}

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add middleware (order matters - last added runs first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    await redis_client.connect()
    print("\n🚀 Trinity AI Intelligence Console Started")
    print(f"📊 API Docs: http://localhost:8090/api/docs")
    print(f"❤️  Health: http://localhost:8090/health/ai\n")

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.disconnect()

BASE_DIR = Path("uploads"); BASE_DIR.mkdir(exist_ok=True)
heavy_orchestrator = TrinityWorkloadOrchestrator()

# ───────────── Helpers ─────────────
def ensure_project(name:str):
    proj = BASE_DIR / name
    (proj / "documents").mkdir(parents=True, exist_ok=True)
    (proj / "snapshots").mkdir(exist_ok=True)
    if not (proj / "config.json").exists():
        (proj / "config.json").write_text(json.dumps({
            "identity":"You are Trinity, an advanced analytical AI."
        }, indent=2))
    if not (proj / "memory.json").exists():
        (proj / "memory.json").write_text("[]")
    return proj

def load_json(path:Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return default

def save_json(path:Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ───────────── Text Extraction ─────────────
def extract_text(path:Path):
    ext = path.suffix.lower()
    try:
        if ext in [".txt",".csv",".json"]: return path.read_text(errors="ignore")[:25000]
        if ext==".pdf":
            text=""
            try:
                reader=PdfReader(str(path))
                for p in reader.pages[:20]: text += p.extract_text() or ""
            except: pass
            if not text.strip():
                doc=fitz.open(str(path))
                for page in doc:
                    text += page.get_text("text") or pytesseract.image_to_string(page.get_pixmap().tobytes())
            return text[:25000] or "(No readable text.)"
        if ext in [".docx",".doc"]:
            doc=Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)[:25000]
        if ext in [".png",".jpg",".jpeg",".bmp",".gif"]:
            img=Image.open(str(path))
            text=pytesseract.image_to_string(img)
            return text or f"Image {img.format}, {img.size[0]}×{img.size[1]} px"
        if ext in [".xlsx"]:
            import openpyxl
            wb=openpyxl.load_workbook(str(path), data_only=True)
            return "\n".join(f"{ws.title}: {list(ws.iter_rows(min_row=1,max_row=2,values_only=True))}"
                             for ws in wb.worksheets)[:25000]
        if ext in [".mp3",".wav",".m4a",".mp4",".mov",".avi",".zip"]:
            return f"Binary file {path.name}, size {path.stat().st_size/1e6:.2f} MB."
        return f"Unsupported type: {ext}"
    except Exception as e:
        return f"Error reading {path.name}: {e}"

# ───────────── AI Engines ─────────────
def run_openai(prompt):
    cli=_openai_client()
    r=cli.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],max_tokens=1500)
    return r.choices[0].message.content.strip()

def run_gemini(prompt):
    cli=_gemini_client()
    r=cli.models.generate_content(model="models/gemini-2.5-pro",contents=prompt)
    return r.text.strip()

def run_anthropic(prompt):
    cli=_anthropic_client()
    r=cli.messages.create(model="claude-sonnet-4-5-20250929",
        messages=[{"role":"user","content":prompt}],max_tokens=1500)
    return r.content[0].text.strip()

def trinity(prompt):
    # Prefer unified orchestrator but fall back to original engine chain on error
    try:
        res = unified_trinity_engine(prompt)
        if isinstance(res, dict):
            return res.get("text", "")
        return str(res)
    except Exception:
        traceback.print_exc()
    # Fallback: original behavior
    for fn in [run_openai, run_gemini, run_anthropic]:
        try:
            txt = fn(prompt)
            if txt and "cannot review" not in txt.lower():
                return txt
        except Exception:
            traceback.print_exc()
    return "⚠️ All engines failed."

@app.get("/health/ai")
def health_ai():
    cfg = get_config()
    status = {
        "gemini": bool(cfg.gemini_api_key),
        "openai": bool(cfg.openai_api_key),
        "anthropic": bool(cfg.anthropic_api_key)
    }
    return {"engines": status, "missing": [k for k, v in status.items() if not v]}

@app.get("/health/live")
def health_live():
    return {"status": "ok"}

@app.get("/health/ready")
def health_ready():
    # Basic readiness: filesystem access to uploads and app imports
    try:
        BASE_DIR.mkdir(exist_ok=True)
        return {"status": "ready"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}

# ───────────── Metrics (Prometheus) ─────────────
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
except Exception:
    generate_latest = CONTENT_TYPE_LATEST = None

@app.get("/metrics")
def metrics():
    if not generate_latest:
        return {"error":"prometheus-client not installed"}
    data = generate_latest()
    from fastapi import Response
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# ───────────── Routes ─────────────
@app.get("/projects")
def list_projects():
    return {"projects":[p.name for p in BASE_DIR.iterdir() if p.is_dir()]}

@app.post("/create_project")
def create_project(name:str=Form(...)):
    ensure_project(name); return {"status":"created","name":name}

@app.get("/project_data/{name}")
def project_data(name:str):
    proj=ensure_project(name)
    cfg=load_json(proj/"config.json",{})
    mem=load_json(proj/"memory.json",[])
    docs=[f.name for f in (proj/"documents").iterdir() if f.is_file()]
    return {"config":cfg,"memory":mem,"documents":docs}

@app.post("/upload/{project}")
async def upload_file(project:str, files:List[UploadFile]=File(...)):
    # Validate files
    validate_files(files)
    for file in files:
        await check_file_size(file)
    
    proj=ensure_project(project)
    results=[]
    for f in files:
        dest=proj/"documents"/f.filename
        with dest.open("wb") as buf: shutil.copyfileobj(f.file,buf)
        text=extract_text(dest)
        summary=trinity(f"Summarize '{f.filename}' in detail:\n{text}")
        results.append({"filename":f.filename,"summary":summary})
        mem=load_json(proj/"memory.json",[])
        mem.append({"time":str(datetime.datetime.now()),"actor":"Trinity",
                    "text":f"Summary of {f.filename}: {summary[:500]}"})
        save_json(proj/"memory.json",mem)
    return {"results":results}

@app.get("/view_summary/{project}/{filename}")
def view_summary(project:str, filename:str):
    proj=ensure_project(project)
    mem=load_json(proj/"memory.json",[])
    for m in reversed(mem):
        if filename in m["text"]: return {"summary":m["text"]}
    return {"summary":"No summary found."}

@app.post("/reanalyze/{project}/{filename}")
def reanalyze(project:str, filename:str):
    proj=ensure_project(project)
    path=proj/"documents"/filename
    if not path.exists(): return {"error":"File not found."}
    text=extract_text(path)
    summary=trinity(f"Reanalyze document '{filename}' thoroughly:\n{text}")
    mem=load_json(proj/"memory.json",[])
    mem.append({"time":str(datetime.datetime.now()),"actor":"Trinity","text":summary})
    save_json(proj/"memory.json",mem)
    return {"summary":summary}

@app.post("/delete_file/{project}/{filename}")
def delete_file(project:str, filename:str):
    proj=ensure_project(project)
    path=proj/"documents"/filename
    if path.exists(): path.unlink()
    return {"deleted":filename}

class ChatReq(BaseModel):
    prompt:str
    system:str


class HeavyWorkloadReq(BaseModel):
    prompt: str
    project: Optional[str] = None

@app.post("/chat/{project}")
def chat(project:str, data:ChatReq):
    proj=ensure_project(project)
    mem=load_json(proj/"memory.json",[])
    cfg=load_json(proj/"config.json",{})
    now=str(datetime.datetime.now())
    context="\n".join(f"[{m['time']}] {m['actor']}: {m['text']}" for m in mem[-10:])
    identity=data.system or cfg.get("identity","You are Trinity.")
    full=f"{identity}\n\n[{now}]\n{context}\nUser: {data.prompt}"
    reply=trinity(full)
    mem.extend([{"time":now,"actor":"User","text":data.prompt},
                {"time":now,"actor":"Trinity","text":reply}])
    save_json(proj/"memory.json",mem)
    return {"text":reply}


@app.post("/orchestrate/heavy")
async def orchestrate_heavy(payload: HeavyWorkloadReq):
    project_context = None
    if payload.project:
        proj = ensure_project(payload.project)
        cfg = load_json(proj/"config.json", {})
        mem = load_json(proj/"memory.json", [])
        recent = "\n".join(f"[{m['time']}] {m['actor']}: {m['text']}" for m in mem[-5:])
        project_context = f"Identity: {cfg.get('identity','Trinity')}\nRecent memory:\n{recent}"
    report = await heavy_orchestrator.run(payload.prompt, project_context)
    response_steps = []
    for step in report.steps:
        result = report.results.get(step.id)
        response_steps.append({
            "id": step.id,
            "intent": step.intent,
            "description": step.description,
            "engine": result.engine if result else None,
            "output": result.text if result else None,
            "confidence": result.confidence if result else None,
            "latency": result.latency if result else None,
            "citations": result.citations if result else [],
            "error": result.error if result else None,
        })
    return {
        "prompt": payload.prompt,
        "final_output": report.final_output,
        "steps": response_steps,
        "timeline": report.timeline,
    }

@app.get("/scan_project/{project}")
def scan_project(project:str):
    proj=ensure_project(project)
    results=[]
    for f in (proj/"documents").iterdir():
        text=extract_text(f)
        summary=trinity(f"Summarize '{f.name}' again:\n{text}")
        results.append({"filename":f.name,"summary":summary})
    return {"results":results}

@app.post("/save_snapshot/{project}")
def save_snapshot(project:str, summary:str=Form("")):
    proj=ensure_project(project)
    snap_dir=proj/"snapshots"; snap_dir.mkdir(exist_ok=True)
    snap_file=snap_dir/f"{datetime.date.today()}.json"
    cfg=load_json(proj/"config.json",{})
    mem=load_json(proj/"memory.json",[])
    data={"timestamp":str(datetime.datetime.now()),"config":cfg,"memory":mem[-20:],
          "summary":summary}
    save_json(snap_file,data)
    return {"snapshot":str(snap_file)}

# ───────────── Static Frontend ─────────────
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# ───────────── WebSocket Chat Streaming ─────────────
@app.websocket("/ws/chat/{project}/{client_id}")
async def websocket_chat(websocket: WebSocket, project: str, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            prompt = data.get("prompt", "")
            system = data.get("system", "")
            
            if not prompt:
                await ws_manager.send_error("Prompt is required", client_id)
                continue
            
            # Process chat with streaming
            proj = ensure_project(project)
            mem = load_json(proj/"memory.json", [])
            cfg = load_json(proj/"config.json", {})
            now = str(datetime.datetime.now())
            context = "\n".join(f"[{m['time']}] {m['actor']}: {m['text']}" for m in mem[-10:])
            identity = system or cfg.get("identity", "You are Trinity.")
            full = f"{identity}\n\n[{now}]\n{context}\nUser: {prompt}"
            
            try:
                # Stream response (simplified - real streaming would chunk the response)
                reply = trinity(full)
                
                # Send in chunks
                chunk_size = 50
                for i in range(0, len(reply), chunk_size):
                    await ws_manager.send_stream_chunk(reply[i:i+chunk_size], client_id)
                    await asyncio.sleep(0.05)  # Small delay for streaming effect
                
                await ws_manager.send_complete(client_id)
                
                # Save to memory
                mem.extend([
                    {"time": now, "actor": "User", "text": prompt},
                    {"time": now, "actor": "Trinity", "text": reply}
                ])
                save_json(proj/"memory.json", mem)
                
            except Exception as e:
                await ws_manager.send_error(str(e), client_id)
    
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)

# Task endpoints moved to /api/v1 router (see routers/v1.py)

# Admin endpoints moved to /api/v1 router (see routers/v1.py)
# Legacy /ops/* endpoints remain for backward compatibility


# ───────────── Rate Limiting Middleware ─────────────
import time as _time
import threading as _threading
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60, window: int = 60, include_paths=None):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.include_paths = set(include_paths or [])
        self._lock = _threading.Lock()
        self._hits = {}  # key: (ip, path) -> list[timestamps]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Only limit selected heavy endpoints
        if self.include_paths and path not in self.include_paths:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        key = (ip, path)
        now = _time.time()
        cutoff = now - self.window

        with self._lock:
            bucket = self._hits.get(key, [])
            # drop old entries
            bucket = [t for t in bucket if t > cutoff]
            if len(bucket) >= self.limit:
                retry_after = int(bucket[0] + self.window - now) + 1
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded", "retry_after": retry_after},
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)
            self._hits[key] = bucket

        return await call_next(request)


# Apply limiter to heavy endpoints only
_RL_PREFIXES = {"/chat/", "/upload/", "/reanalyze/", "/scan_project/"}

class _PrefixRateLimiter(RateLimiterMiddleware):
    async def dispatch(self, request: Request, call_next):
        # If path starts with any configured prefix, apply limiting
        if any(str(request.url.path).startswith(p) for p in _RL_PREFIXES):
            return await super().dispatch(request, call_next)
        return await call_next(request)

app.add_middleware(_PrefixRateLimiter, limit=60, window=60, include_paths=list(_RL_PREFIXES))
