#!/usr/bin/env python3
"""
Multi-System Orchestration Verification Script
Checks all services and validates integration
"""

import subprocess
import json
import time
import sys
from typing import Dict, Tuple

class SystemVerifier:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'services': {},
            'integration': {},
            'errors': []
        }
    
    def check_port(self, host: str, port: int, name: str) -> Tuple[bool, str]:
        """Check if a service is running on a port"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return True, f"✅ {name} running on {host}:{port}"
            else:
                return False, f"❌ {name} not responding on {host}:{port}"
        except Exception as e:
            return False, f"❌ {name} check failed: {str(e)}"
    
    def check_api_endpoint(self, url: str, name: str) -> Tuple[bool, str]:
        """Check if an API endpoint is responsive"""
        try:
            import urllib.request
            response = urllib.request.urlopen(url, timeout=3)
            if response.status == 200:
                return True, f"✅ {name} responding at {url}"
            else:
                return False, f"⚠️  {name} returned status {response.status}"
        except Exception as e:
            return False, f"❌ {name} failed: {str(e)}"
    
    def validate_systems(self):
        """Run all validation checks"""
        print("\n" + "="*70)
        print("🔍 MULTI-SYSTEM ORCHESTRATION VERIFICATION")
        print("="*70 + "\n")
        
        # YUR Agent Portal
        print("📦 YUR Agent Portal:")
        print("-" * 70)
        checks = [
            (8080, "Marketplace Service"),
            (3000, "Express Backend API"),
            (3001, "React Frontend"),
            (5000, "PyQMC Service")
        ]
        for port, name in checks:
            passed, msg = self.check_port('localhost', port, name)
            print(msg)
            self.results['services'][f"yur_{port}"] = passed
        
        # SOVEREIGN AI
        print("\n🤖 SOVEREIGN AI System:")
        print("-" * 70)
        checks = [
            (8000, "FastAPI Backend"),
            (5173, "Vite Frontend")
        ]
        for port, name in checks:
            passed, msg = self.check_port('localhost', port, name)
            print(msg)
            self.results['services'][f"sovereign_{port}"] = passed
        
        # Integration Bridge
        print("\n🌉 Integration Bridge:")
        print("-" * 70)
        passed, msg = self.check_port('localhost', 8001, "Integration Bridge")
        print(msg)
        self.results['services']['bridge_8001'] = passed
        
        # API Endpoints
        print("\n🔗 API Endpoints:")
        print("-" * 70)
        
        # Bridge health
        passed, msg = self.check_api_endpoint('http://localhost:8001/health', 'Bridge /health')
        print(msg)
        self.results['integration']['bridge_health'] = passed
        
        if passed:
            try:
                import urllib.request
                response = urllib.request.urlopen('http://localhost:8001/health', timeout=3)
                data = json.loads(response.read().decode())
                print(f"  YUR Status: {data.get('yur_status', 'unknown')}")
                print(f"  SOVEREIGN Status: {data.get('sovereign_status', 'unknown')}")
                print(f"  Active Tasks: {data.get('active_tasks', 0)}")
                print(f"  System Uptime: {data.get('system_uptime_seconds', 0):.1f}s")
            except Exception as e:
                self.results['errors'].append(f"Could not parse bridge health: {str(e)}")
        
        # YUR Agents endpoint
        passed, msg = self.check_api_endpoint('http://localhost:3000/api/agents', 'YUR /api/agents')
        print(msg)
        self.results['integration']['yur_agents'] = passed
        
        # Summary
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        
        all_services = list(self.results['services'].values())
        all_integration = list(self.results['integration'].values())
        
        passed_services = sum(all_services)
        passed_integration = sum(all_integration)
        
        print(f"Services: {passed_services}/{len(all_services)} operational")
        print(f"Integration: {passed_integration}/{len(all_integration)} functional")
        
        if len(self.results['errors']) > 0:
            print(f"\n⚠️  Errors detected:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Overall status
        overall_healthy = (passed_services >= 5 and passed_integration >= 2)
        status = "✅ READY FOR DEPLOYMENT" if overall_healthy else "❌ REQUIRES ATTENTION"
        print(f"\n🎯 Overall Status: {status}\n")
        
        return overall_healthy
    
    def export_report(self):
        """Export verification report as JSON"""
        filename = f"verification_report_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Report saved: {filename}")
        return filename

def main():
    verifier = SystemVerifier()
    
    print("\n🚀 Starting Multi-System Verification...\n")
    time.sleep(1)
    
    healthy = verifier.validate_systems()
    verifier.export_report()
    
    if healthy:
        print("\n✨ All systems operational! Access the UI at: http://localhost:5173")
        print("   Navigate to 'Unified Orchestrator' in the left sidebar to begin.\n")
        sys.exit(0)
    else:
        print("\n⚠️  Some systems need attention. See above for details.\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
