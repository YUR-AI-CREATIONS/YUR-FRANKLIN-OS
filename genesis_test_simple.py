#!/usr/bin/env python3
"""
Simple Genesis Pipeline v2.0 API Testing (without LLM calls)
"""

import requests
import json
import sys
from datetime import datetime

class SimpleGenesisTest:
    def __init__(self, base_url="https://franklinos.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.project_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")

    def test_api_root(self):
        """Test API root for v2.0 and modules"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check version
                version = data.get('version', '')
                if version == '2.0.0':
                    self.log_test("API Version 2.0", True, f"Version: {version}")
                else:
                    self.log_test("API Version 2.0", False, f"Expected 2.0.0, got {version}")
                
                # Check modules
                modules = data.get('modules', [])
                expected_modules = [
                    "Socratic Engine", "Genesis Kernel", "Ouroboros Loop", 
                    "Quality Gate", "Governance Engine", "Multi-Kernel Orchestrator"
                ]
                
                if len(modules) >= 6 and all(mod in modules for mod in expected_modules):
                    self.log_test("All 6 Modules Listed", True, f"Found: {modules}")
                else:
                    self.log_test("All 6 Modules Listed", False, f"Expected {expected_modules}, got {modules}")
                    
                return True
            else:
                self.log_test("API Root", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root", False, str(e))
            return False

    def test_genesis_project_init(self):
        """Test project initialization"""
        try:
            response = requests.post(
                f"{self.api_url}/genesis/project/init",
                json={
                    "name": "Test Genesis Project",
                    "description": "Testing the Genesis Pipeline v2.0"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.project_id = data.get("orchestrator_id")
                
                # Check required fields
                required_fields = ["orchestrator_id", "primary_kernel_id", "agents", "status"]
                if all(field in data for field in required_fields):
                    agents = data.get("agents", [])
                    self.log_test("Genesis Project Init", True, f"Project initialized with {len(agents)} agents")
                    return data
                else:
                    self.log_test("Genesis Project Init", False, "Missing required fields")
            else:
                self.log_test("Genesis Project Init", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Genesis Project Init", False, str(e))
        return {}

    def test_quality_assessment(self):
        """Test quality assessment"""
        test_artifact = {
            "name": "Test System",
            "components": ["auth", "api", "database"],
            "security": {"authentication": "oauth2", "encryption": "aes256"}
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/genesis/quality/assess",
                json={
                    "artifact": test_artifact,
                    "stage": "architecture"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                dimensions = data.get("dimension_scores", [])
                score = data.get("aggregate_score", 0)
                
                if len(dimensions) == 8:
                    self.log_test("8-Dimensional Quality Assessment", True, f"Score: {score}%")
                else:
                    self.log_test("8-Dimensional Quality Assessment", False, f"Expected 8 dimensions, got {len(dimensions)}")
                return data
            else:
                self.log_test("Quality Assessment", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Quality Assessment", False, str(e))
        return {}

    def test_compliance_audit(self):
        """Test compliance audit"""
        test_artifact = {
            "security": {
                "authentication": "oauth2",
                "encryption": {"at_rest": "aes256", "in_transit": "tls13"}
            },
            "features": {"audit_log": True}
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/governance/compliance/audit",
                json={
                    "artifact": test_artifact,
                    "categories": ["security", "data_privacy"]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                score = data.get("compliance_score", 0)
                self.log_test("Compliance Audit", True, f"Compliance score: {score}%")
                return data
            else:
                self.log_test("Compliance Audit", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Compliance Audit", False, str(e))
        return {}

    def test_license_configuration(self):
        """Test license configuration"""
        try:
            response = requests.post(
                f"{self.api_url}/governance/license/configure",
                json={
                    "license_type": "open_source",
                    "custom_terms": {"governing_law": "State of California, USA"}
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                license_type = data.get("license_type")
                document = data.get("document", "")
                
                if license_type == "open_source" and len(document) > 100:
                    self.log_test("License Configuration", True, f"Generated {len(document)} char document")
                else:
                    self.log_test("License Configuration", False, "Invalid license or document")
                return data
            else:
                self.log_test("License Configuration", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("License Configuration", False, str(e))
        return {}

    def test_orchestrator_agents(self):
        """Test agent listing"""
        try:
            response = requests.get(f"{self.api_url}/orchestrator/agents", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                
                if len(agents) > 0:
                    agent_tiers = [agent.get("tier") for agent in agents]
                    expected_tiers = ["commander", "architect", "builder", "validator", "guardian", "executor"]
                    found_tiers = [tier for tier in expected_tiers if tier in agent_tiers]
                    
                    if len(found_tiers) >= 6:
                        self.log_test("Orchestrator Agents", True, f"Found {len(agents)} agents with all tiers")
                    else:
                        self.log_test("Orchestrator Agents", False, f"Missing tiers: {found_tiers}")
                else:
                    self.log_test("Orchestrator Agents", False, "No agents found")
                return data
            else:
                self.log_test("Orchestrator Agents", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Orchestrator Agents", False, str(e))
        return {}

    def test_page_generation(self):
        """Test page generation"""
        if not self.project_id:
            self.log_test("Page Generation", False, "No project initialized")
            return {}
        
        test_spec = {
            "name": "Test App",
            "features": ["auth", "dashboard"],
            "components": [{"name": "User Management", "type": "crud"}]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/orchestrator/pages/generate",
                json={
                    "project_id": self.project_id,
                    "specification": test_spec
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                total_pages = data.get("total_pages", 0)
                structure = data.get("structure", {})
                
                if total_pages >= 10 and len(structure) >= 4:
                    self.log_test("Page Generation", True, f"Generated {total_pages} pages")
                else:
                    self.log_test("Page Generation", False, f"Too few pages: {total_pages}")
                return data
            else:
                self.log_test("Page Generation", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Page Generation", False, str(e))
        return {}

    def run_tests(self):
        """Run all tests"""
        print("🚀 Testing Genesis Pipeline v2.0 Core Features")
        print("=" * 50)
        
        # Test basic API
        if not self.test_api_root():
            print("❌ API not accessible")
            return
        
        # Test Genesis features
        self.test_genesis_project_init()
        self.test_quality_assessment()
        self.test_compliance_audit()
        self.test_license_configuration()
        self.test_orchestrator_agents()
        self.test_page_generation()
        
        # Summary
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print("\n" + "=" * 50)
        print(f"📊 Results: {self.tests_passed}/{self.tests_run} passed ({success_rate:.1f}%)")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Genesis v2.0 features working!")
        else:
            print("⚠️  Some features need attention")

if __name__ == "__main__":
    tester = SimpleGenesisTest()
    tester.run_tests()