"""
Trinity Mothership Orchestrator
- Registers available multimodal handlers with `trinity_orchestrator_unified`.
- Provides a small CLI to register and start services.

Usage examples:
    python trinity_mothership.py --register
    python trinity_mothership.py --run-smoke
    python trinity_mothership.py --start-api 8080
"""
import subprocess
import sys
import argparse
from trinity_orchestrator_unified import register_handler

# Import gemini handlers (module is import-safe now)
import gemini_master


def _gemini_dispatch(prompt: str, max_tokens: int = 600, clients=None):
    """Dispatch Gemini multimodal requests to the appropriate gemini_master function."""
    lower = prompt.lower()
    try:
        if any(k in lower for k in ["image","render","visualize","scene","photo","picture"]):
            return gemini_master.generate_image(prompt)
        if any(k in lower for k in ["video","movie","clip","animation"]):
            return gemini_master.generate_video(prompt)
        if any(k in lower for k in ["audio","speak","say","read aloud","tts"]):
            return gemini_master.generate_audio(prompt)
        if any(k in lower for k in ["embed","vector","embedding"]):
            return gemini_master.generate_embedding(prompt)
        # default to text generation
        return gemini_master.generate_text(prompt)
    except Exception as e:
        raise


def register_all():
    register_handler("Gemini", _gemini_dispatch)
    # Also register explicit specialized handler aliases
    try:
        register_handler("GeminiImage", gemini_master.generate_image)
        register_handler("GeminiVideo", gemini_master.generate_video)
        register_handler("GeminiAudio", gemini_master.generate_audio)
        register_handler("GeminiEmbed", gemini_master.generate_embedding)
    except Exception:
        # If gemini_master functions unavailable, ignore — core Gemini dispatch still registered
        pass
    print("Registered Gemini dispatch handler (plus specialized aliases) with unified orchestrator.")


def run_smoke():
    # Invoke existing smoke_test.py to regenerate reports
    subprocess.check_call([sys.executable, "smoke_test.py"], cwd='.')


def start_api(port: int = 8080):
    # Start uvicorn app:app
    print(f"Starting FastAPI on port {port} (uvicorn). Use CTRL+C to stop.")
    subprocess.check_call([sys.executable, "-m", "uvicorn", "app:app", "--port", str(port)])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--register", action="store_true")
    p.add_argument("--run-smoke", action="store_true")
    p.add_argument("--start-api", type=int, help="Start FastAPI on given port")
    args = p.parse_args()

    if args.register:
        register_all()
    if args.run_smoke:
        register_all()
        run_smoke()
    if args.start_api:
        register_all()
        start_api(args.start_api)


if __name__ == "__main__":
    main()
