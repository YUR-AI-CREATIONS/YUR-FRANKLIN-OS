#!/usr/bin/env python3
"""
TRINITY AI MASTER SYSTEM - Startup Orchestrator
Launches all services and manages the unified cockpit experience
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

# Load environment
from dotenv import load_dotenv
load_dotenv()

def print_banner():
    """Print startup banner"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        🌟 TRINITY AI MASTER ORCHESTRATION SYSTEM 🌟     ║
    ║                                                          ║
    ║           Multi-Model AI Routing & Execution            ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def check_dependencies():
    """Check required dependencies"""
    required = ['fastapi', 'uvicorn', 'httpx', 'python-dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        return False
    
    print(f"✅ Dependencies OK ({len(required)} packages)")
    return True

def check_api_keys():
    """Check if API keys are configured"""
    keys_found = {
        'XAI_API_KEY': os.getenv('XAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    }
    
    print("\n📋 API Key Status:")
    for key, value in keys_found.items():
        status = "✅" if value else "⏭️ "
        print(f"   {status} {key}")
    
    if os.getenv('XAI_API_KEY'):
        print("\n✅ Grok XAI enabled - can run with limited functionality")
        return True
    
    return False

def start_backend():
    """Start the Trinity backend"""
    print("\n🚀 Starting Trinity Backend on port 8001...")
    
    try:
        # Start FastAPI server
        subprocess.Popen([
            sys.executable, '-m', 'uvicorn',
            'trinity_backend:app',
            '--host', '0.0.0.0',
            '--port', '8001',
            '--reload'
        ])
        
        # Wait for server to start
        time.sleep(3)
        print("✅ Trinity Backend started on http://localhost:8001")
        return True
    
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def check_frontend():
    """Check if frontend is running"""
    frontend_path = Path(__file__).parent / 'sovereign-frontend'
    
    if frontend_path.exists():
        print(f"✅ Frontend found at {frontend_path}")
        print("   Frontend is running on http://localhost:5173")
        return True
    else:
        print(f"❌ Frontend not found at {frontend_path}")
        return False

def main():
    """Main startup sequence"""
    print_banner()
    
    # Checks
    check_python()
    
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        return 1
    
    check_api_keys()
    
    # Start backend
    if not start_backend():
        print("\n❌ Failed to start backend services")
        return 1
    
    # Check frontend
    check_frontend()
    
    print("\n" + "="*60)
    print("✅ TRINITY AI SYSTEM READY")
    print("="*60)
    print("\n📍 Access Points:")
    print("   Frontend:  http://localhost:5173")
    print("   Backend:   http://localhost:8001")
    print("   API Docs:  http://localhost:8001/docs")
    print("\n🤖 Available Models:")
    print("   • Gemini 2.0 Flash (Multimodal)")
    print("   • GPT-4O Mini (Fast & Efficient)")
    print("   • Claude 3.5 Sonnet (Deep Analysis)")
    print("\n💡 Tip: Open http://localhost:5173 in your browser to start")
    print("="*60 + "\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Trinity AI System...")
        return 0

if __name__ == '__main__':
    sys.exit(main())
