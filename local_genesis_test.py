#!/usr/bin/env python3
"""
Local Genesis Pipeline v2.0 API Testing
"""

import requests
import json
import sys
from datetime import datetime

def test_local_api():
    """Test local API endpoints"""
    base_url = "http://localhost:8001"
    
    print("🚀 Testing Genesis Pipeline v2.0 Locally")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: API Root
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/api/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', '')
            modules = data.get('modules', [])
            
            if version == '2.0.0' and len(modules) >= 6:
                print(f"✅ API Root - v{version} with {len(modules)} modules")
                tests_passed += 1
            else:
                print(f"❌ API Root - Version: {version}, Modules: {len(modules)}")
        else:
            print(f"❌ API Root - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API Root - {str(e)}")
    
    # Test 2: Genesis Project Init
    tests_total += 1
    project_id = None
    try:
        response = requests.post(
            f"{base_url}/api/genesis/project/init",
            json={"name": "Test Project", "description": "Test"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            project_id = data.get("orchestrator_id")
            agents = data.get("agents", [])
            print(f"✅ Genesis Project Init - {len(agents)} agents initialized")
            tests_passed += 1
        else:
            print(f"❌ Genesis Project Init - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Genesis Project Init - {str(e)}")
    
    # Test 3: Quality Assessment
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/api/genesis/quality/assess",
            json={
                "artifact": {"name": "Test", "components": ["auth"]},
                "stage": "architecture"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            dimensions = data.get("dimension_scores", [])
            score = data.get("aggregate_score", 0)
            print(f"✅ Quality Assessment - {len(dimensions)} dimensions, score: {score}%")
            tests_passed += 1
        else:
            print(f"❌ Quality Assessment - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Quality Assessment - {str(e)}")
    
    # Test 4: Compliance Audit
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/api/governance/compliance/audit",
            json={
                "artifact": {"security": {"authentication": "oauth2"}},
                "categories": ["security"]
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            score = data.get("compliance_score", 0)
            print(f"✅ Compliance Audit - Score: {score}%")
            tests_passed += 1
        else:
            print(f"❌ Compliance Audit - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Compliance Audit - {str(e)}")
    
    # Test 5: License Configuration
    tests_total += 1
    try:
        response = requests.post(
            f"{base_url}/api/governance/license/configure",
            json={"license_type": "open_source"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            license_type = data.get("license_type")
            print(f"✅ License Configuration - Type: {license_type}")
            tests_passed += 1
        else:
            print(f"❌ License Configuration - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ License Configuration - {str(e)}")
    
    # Test 6: Orchestrator Agents
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/api/orchestrator/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            print(f"✅ Orchestrator Agents - {len(agents)} agents listed")
            tests_passed += 1
        else:
            print(f"❌ Orchestrator Agents - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Orchestrator Agents - {str(e)}")
    
    # Summary
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    print("\n" + "=" * 50)
    print(f"📊 Results: {tests_passed}/{tests_total} passed ({success_rate:.1f}%)")
    
    return tests_passed, tests_total

if __name__ == "__main__":
    test_local_api()