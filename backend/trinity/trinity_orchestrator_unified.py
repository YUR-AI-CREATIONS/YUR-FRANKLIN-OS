"""
Unified Trinity Orchestrator
Provides: routing, engine wrappers (Gemini/OpenAI/Anthropic), failover, telemetry, and a simple CLI.

This module is written to be import-safe: external SDKs are optionally imported
so a developer can `import` the module without API keys installed. Engines are
created lazily when first used.
"""
import os
import time
import json
import traceback
from typing import Optional
from telemetry import record_request, record_success, record_failure

# Optional imports (import-safe)
try:
    from google import genai
except Exception:
    genai = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import anthropic
except Exception:
    anthropic = None

# Optional config import (centralized env access)
try:
    from config import get_config
except Exception:
    get_config = None


def _make_clients():
    """Lazily create API clients from environment variables (via config if available)."""
    clients = {}
    if get_config:
        cfg = get_config()
        gemini_key = cfg.gemini_api_key
        openai_key = cfg.openai_api_key
        anthropic_key = cfg.anthropic_api_key
        missing = cfg.missing_keys()
        if missing:
            print(f"[TrinityConfig] Missing keys: {', '.join(missing)} (engines without keys will be skipped)")
    else:
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if genai and gemini_key:
        clients["gemini"] = genai.Client(api_key=gemini_key)
    if OpenAI and openai_key:
        clients["openai"] = OpenAI(api_key=openai_key)
    if anthropic and anthropic_key:
        clients["anthropic"] = anthropic.Anthropic(api_key=anthropic_key)

    return clients


# --- Plugin / handler registry ---
# Allows other modules to register handlers for engine kinds (e.g., Gemini image/video handlers)
_HANDLER_REGISTRY = {}


def register_handler(kind: str, func):
    """Register a handler function for a given engine kind.

    Handler signature should be: func(prompt: str, max_tokens: int = 600, clients: Optional[dict] = None) -> dict
    """
    _HANDLER_REGISTRY[kind] = func


def get_handler(kind: str):
    return _HANDLER_REGISTRY.get(kind)


def classify_prompt(prompt: str) -> str:
    lower = prompt.lower()
    if any(k in lower for k in ["image", "video", "render", "design", "visualize"]):
        return "Gemini"
    if any(k in lower for k in ["analyze", "summarize", "compare", "calculate", "data"]):
        return "OpenAI"
    if any(k in lower for k in ["philosophy", "ethics", "meaning", "law", "spiritual"]):
        return "Anthropic"
    return "OpenAI"


def run_gemini(prompt: str, max_tokens: int = 600, clients: Optional[dict] = None):
    start = time.time()
    clients = clients or _make_clients()
    if "gemini" not in clients:
        raise RuntimeError("Gemini client not available (missing package or GEMINI_API_KEY).")
    client = clients["gemini"]
    r = client.models.generate_content(model="models/gemini-2.5-pro", contents=prompt)
    text = getattr(r, "text", None) or getattr(r, "output", None) or str(r)
    return {"engine": "Gemini", "text": text.strip(), "latency": round(time.time() - start, 2), "confidence": 0.9}


def run_openai(prompt: str, max_tokens: int = 600, clients: Optional[dict] = None):
    start = time.time()
    clients = clients or _make_clients()
    if "openai" not in clients:
        raise RuntimeError("OpenAI client not available (missing package or OPENAI_API_KEY).")
    client = clients["openai"]
    r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens)
    text = r.choices[0].message.content.strip()
    return {"engine": "OpenAI", "text": text, "latency": round(time.time() - start, 2), "confidence": 0.92}


def run_anthropic(prompt: str, max_tokens: int = 600, clients: Optional[dict] = None):
    start = time.time()
    clients = clients or _make_clients()
    if "anthropic" not in clients:
        raise RuntimeError("Anthropic client not available (missing package or ANTHROPIC_API_KEY).")
    client = clients["anthropic"]
    r = client.messages.create(model="claude-sonnet-4-5-20250929", max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])
    text = r.content[0].text.strip()
    return {"engine": "Anthropic", "text": text, "latency": round(time.time() - start, 2), "confidence": 0.88}


def trinity_engine(prompt: str, max_tokens: int = 600, log_file: str = "trinity_log.json"):
    record_request(prompt)
    primary = classify_prompt(prompt)
    engines = {"Gemini": run_gemini, "OpenAI": run_openai, "Anthropic": run_anthropic}
    ordered = [primary] + [e for e in engines if e != primary]

    log_entry = {"prompt": prompt, "results": [], "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    clients = _make_clients()

    for engine in ordered:
        try:
            print(f"\n🚀 Routing to {engine}...")
            # allow registered handlers to override built-ins
            fn = get_handler(engine) or engines[engine]
            result = fn(prompt, max_tokens=max_tokens, clients=clients)
            print(f"✅ {engine} succeeded in {result['latency']}s")
            log_entry["results"].append(result)
            record_success(engine, result['latency'])
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return result
        except Exception as e:
            print(f"⚠️ {engine} failed: {type(e).__name__} - {e}")
            traceback.print_exc()
            log_entry["results"].append({"engine": engine, "error": str(e)})
            record_failure(engine, str(e))
            continue

    raise RuntimeError("❌ All engines failed.")


def _cli():
    import argparse
    p = argparse.ArgumentParser(description="Trinity Unified Orchestrator CLI")
    p.add_argument("--prompt", "-p", type=str, required=True, help="Prompt text to send")
    p.add_argument("--max-tokens", type=int, default=600, help="Max tokens for completion")
    args = p.parse_args()
    res = trinity_engine(args.prompt, max_tokens=args.max_tokens)
    print("\n--- FINAL OUTPUT ---")
    print(f"Source: {res['engine']} | Latency: {res['latency']}s | Confidence: {res.get('confidence')}")
    print(res['text'])


if __name__ == "__main__":
    _cli()
