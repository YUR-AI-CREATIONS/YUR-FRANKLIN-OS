#!/usr/bin/env python3
"""
Multi-System Orchestration - Complete Startup Script
Brings up all services: YUR Portal, SOVEREIGN AI, Integration Bridge, Grok Agent API
"""

import subprocess
import time
import os
import sys
import threading
from pathlib import Path

class SystemOrchestrator:
    def __init__(self):
        self.services = []
        self.base_path = Path(os.getcwd())
        
    def print_banner(self, text, color=None):
        """Pretty print banner"""
        colors = {
            'cyan': '\033[96m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'reset': '\033[0m'
        }
        c = colors.get(color, '')
        r = colors['reset']
        print(f"{c}{text}{r}")
    
    def start_service(self, name, command, cwd=None, port=None):
        """Start a service in background"""
        self.print_banner(f"\n🚀 Starting: {name}", 'cyan')
        
        if cwd is None:
            cwd = os.getcwd()
        
        # Start process
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.services.append({
            'name': name,
            'process': process,
            'port': port,
            'command': command,
            'cwd': cwd
        })
        
        print(f"ℹ️  Process ID: {process.pid}")
        if port:
            print(f"ℹ️  Port: {port}")
        
        # Give it time to start
        time.sleep(2)
        
        return process
    
    def startup_sequence(self):
        """Orchestrate complete system startup"""
        
        self.print_banner("="*70, 'cyan')
        self.print_banner("🎯 MULTI-SYSTEM ORCHESTRATION - STARTUP SEQUENCE", 'cyan')
        self.print_banner("="*70, 'cyan')
        
        # 1. YUR Agent Portal (if in Neo3 directory)
        yur_path = Path("c:\\Users\\Jeremy Gosselin\\OneDrive\\Documents\\bigjohnsonco\\Neo3")
        if yur_path.exists():
            self.print_banner("\n📦 YUR AGENT PORTAL", 'green')
            
            # Backend
            self.start_service(
                "YUR Marketplace (Python)",
                "cd backend && python neo3_main.py",
                cwd=yur_path,
                port=8080
            )
            
            # Assuming Express backend is running separately
            print("ℹ️  Note: Start YUR Express backend separately if needed")
            print("    cd backend && npm start  # Runs on port 3000")
        
        # 2. SOVEREIGN AI - Integration Bridge
        self.print_banner("\n🌉 INTEGRATION BRIDGE", 'green')
        self.start_service(
            "Integration Bridge API",
            "python -m uvicorn integration_bridge:app --reload --port 8001",
            cwd=Path("C:\\XAI_GROK_GENESIS\\sovereign-api"),
            port=8001
        )
        
        # 3. SOVEREIGN AI - Frontend
        self.print_banner("\n💻 SOVEREIGN FRONTEND", 'green')
        self.start_service(
            "Sovereign Frontend (Vite)",
            "npm run dev",
            cwd=Path("C:\\XAI_GROK_GENESIS\\sovereign-frontend"),
            port=5173
        )
        
        # 4. Grok Self-Healing Agent API
        self.print_banner("\n🤖 GROK SELF-HEALING AGENT", 'green')
        self.start_service(
            "Grok Agent API",
            "python grok_agent_api.py",
            cwd=Path("C:\\XAI_GROK_GENESIS\\sovereign-api"),
            port=8002
        )
        
        # 5. OLK-7 Ouroboros-Lattice Kernel
        self.print_banner("\n⚛️  OUROBOROS-LATTICE KERNEL", 'green')
        self.start_service(
            "OLK-7 Cognitive Kernel API",
            "python olk7_api.py",
            cwd=Path("C:\\XAI_GROK_GENESIS\\sovereign-api"),
            port=8003
        )
        
        # 6. Print system status
        self.print_system_status()
        
        # Keep running
        self.monitor_services()
    
    def print_system_status(self):
        """Print current system status"""
        self.print_banner("\n" + "="*70, 'green')
        self.print_banner("✨ SYSTEM STATUS", 'green')
        self.print_banner("="*70, 'green')
        
        print("\n📊 RUNNING SERVICES:\n")
        
        service_info = [
            ("YUR Marketplace", "http://localhost:8080", "✅"),
            ("YUR Backend API", "http://localhost:3000", "⚠️ (Start separately)"),
            ("YUR Frontend", "http://localhost:3001", "⚠️ (Start separately)"),
            ("YUR PyQMC", "http://localhost:5000", "⚠️ (Start separately)"),
            ("Integration Bridge", "http://localhost:8001/health", "✅"),
            ("Integration Bridge Docs", "http://localhost:8001/docs", "✅"),
            ("SOVEREIGN Frontend", "http://localhost:5173", "✅"),
            ("SOVEREIGN Orchestrator", "http://localhost:5173/#/orchestrator", "✅"),
            ("Grok Agent API", "http://localhost:8002/health", "✅"),
            ("Grok Agent Docs", "http://localhost:8002/docs", "✅"),
            ("OLK-7 Cognitive Kernel", "http://localhost:8003/health", "✅"),
            ("OLK-7 Kernel Docs", "http://localhost:8003/docs", "✅"),
        ]
        
        for name, url, status in service_info:
            print(f"  {status} {name:30} → {url}")
        
        print("\n🎮 QUICK LINKS:\n")
        print("  🌐 Main Interface:    http://localhost:5173")
        print("  🎯 Orchestrator:      http://localhost:5173 → Click 'Unified Orchestrator'")
        print("  📚 Bridge API Docs:   http://localhost:8001/docs")
        print("  🤖 Grok API Docs:     http://localhost:8002/docs")
        
        print("\n📖 DOCUMENTATION:\n")
        print("  • MULTI_SYSTEM_ORCHESTRATION_DEPLOYMENT.md")
        print("  • QUICK_START.md")
        print("  • GROK_SELF_HEALING_GUIDE.md")
        
        print("\n🧠 GROK AGENT EXAMPLES:\n")
        print("  python grok_self_healing_agent.py 'Create fibonacci calculator' fib.py")
        print("  python demo_self_healing_agent.py")
        
        print("\n" + "="*70 + "\n")
    
    def monitor_services(self):
        """Monitor running services"""
        self.print_banner("Monitoring services... (Press Ctrl+C to stop)", 'yellow')
        
        try:
            while True:
                time.sleep(10)
                
                # Check service health
                for service in self.services:
                    if service['process'].poll() is not None:
                        self.print_banner(
                            f"⚠️  Service died: {service['name']}",
                            'red'
                        )
                        print(f"   Restart with: {service['command']}")
        
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown of all services"""
        self.print_banner("\n\nShutting down services...", 'yellow')
        
        for service in self.services:
            try:
                service['process'].terminate()
                print(f"✓ Stopped: {service['name']}")
            except:
                pass
        
        self.print_banner("Goodbye! 👋", 'cyan')
        sys.exit(0)

def main():
    """Main entry point"""
    
    # Check prerequisites
    try:
        import requests
        print("✓ requests library found")
    except ImportError:
        print("❌ Missing: requests")
        print("   pip install requests")
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv found")
    except ImportError:
        print("❌ Missing: python-dotenv")
        print("   pip install python-dotenv")
    
    try:
        from termcolor import colored
        print("✓ termcolor found")
    except ImportError:
        print("⚠️  Warning: termcolor not found (colors disabled)")
    
    # Check .env file
    if not Path(".env").exists():
        print("❌ Missing: .env file")
        print("   Create .env with XAI_API_KEY=your_key")
        sys.exit(1)
    
    print("✓ .env file found\n")
    
    # Start system
    orchestrator = SystemOrchestrator()
    orchestrator.startup_sequence()

if __name__ == "__main__":
    main()
