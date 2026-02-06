#!/usr/bin/env python3
"""
Sovereign Genesis Platform (SGP) v2.0 Backend API Testing
Tests the Genesis Pipeline with Ouroboros Loop, Quality Gate, Governance Engine, 
Multi-Kernel Orchestrator, and Socratic Pre-Prompt Engine
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

class SGPAPITester:
    def __init__(self, base_url="https://genesis-platform-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
        self.project_id = None
        self.orchestrator_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_api_health(self) -> bool:
        """Test basic API connectivity and v2.0 modules"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" - {data.get('message', 'No message')}"
                
                # Check v2.0 version
                version = data.get('version', '')
                if version == '2.0.0':
                    self.log_test("API Version 2.0", True, f"Version: {version}")
                else:
                    self.log_test("API Version 2.0", False, f"Expected 2.0.0, got {version}")
                
                # Check all 6 modules are listed
                modules = data.get('modules', [])
                expected_modules = [
                    "Socratic Engine", "Genesis Kernel", "Ouroboros Loop", 
                    "Quality Gate", "Governance Engine", "Multi-Kernel Orchestrator"
                ]
                
                if len(modules) >= 6 and all(mod in modules for mod in expected_modules):
                    self.log_test("All 6 Modules Listed", True, f"Found: {modules}")
                else:
                    self.log_test("All 6 Modules Listed", False, f"Expected {expected_modules}, got {modules}")
                    
            self.log_test("API Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
            return False

    def test_analyze_endpoint(self) -> Dict[str, Any]:
        """Test the /analyze endpoint - core Socratic Engine functionality"""
        test_prompt = "Build a user authentication system for a web application"
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze",
                json={"prompt": test_prompt},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log_test("Analyze Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify required fields
            required_fields = ["session_id", "analysis", "confidence_score", "can_proceed"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_test("Analyze Endpoint", False, f"Missing fields: {missing_fields}")
                return {}
            
            # Store session_id for subsequent tests
            self.session_id = data["session_id"]
            
            # Verify Socratic behavior - should NOT proceed directly
            analysis = data["analysis"]
            if data.get("can_proceed", True):
                self.log_test("Socratic Engine Behavior", False, "Engine proceeded directly instead of asking questions")
            else:
                self.log_test("Socratic Engine Behavior", True, "Correctly refused direct answer")
            
            # Verify ambiguities structure
            ambiguities = analysis.get("ambiguities", [])
            if not ambiguities:
                self.log_test("Ambiguities Detection", False, "No ambiguities detected")
            else:
                # Check ambiguity structure
                first_amb = ambiguities[0]
                required_amb_fields = ["id", "category", "question", "options", "priority"]
                missing_amb_fields = [f for f in required_amb_fields if f not in first_amb]
                if missing_amb_fields:
                    self.log_test("Ambiguity Structure", False, f"Missing fields: {missing_amb_fields}")
                else:
                    self.log_test("Ambiguity Structure", True, f"Found {len(ambiguities)} well-formed ambiguities")
            
            # Verify confidence score
            confidence = data.get("confidence_score", 100)
            if confidence >= 99.5:
                self.log_test("Initial Confidence Score", False, f"Confidence too high: {confidence}% (should be low initially)")
            else:
                self.log_test("Initial Confidence Score", True, f"Appropriate low confidence: {confidence}%")
            
            self.log_test("Analyze Endpoint", True, f"Session {self.session_id} created with {len(ambiguities)} ambiguities")
            return data
            
        except Exception as e:
            self.log_test("Analyze Endpoint", False, str(e))
            return {}

    def test_resolve_endpoint(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test the /resolve endpoint"""
        if not self.session_id or not analysis_data:
            self.log_test("Resolve Endpoint", False, "No session or analysis data available")
            return {}
        
        ambiguities = analysis_data.get("analysis", {}).get("ambiguities", [])
        if not ambiguities:
            self.log_test("Resolve Endpoint", False, "No ambiguities to resolve")
            return {}
        
        # Create sample answers for first few ambiguities
        answers = []
        for i, amb in enumerate(ambiguities[:3]):  # Answer first 3 ambiguities
            if amb.get("options"):
                # Select first option if available
                answers.append({
                    "ambiguity_id": amb["id"],
                    "answer": amb["options"][0],
                    "selected_option": amb["options"][0]
                })
            else:
                # Provide a generic answer
                answers.append({
                    "ambiguity_id": amb["id"],
                    "answer": "Standard implementation approach",
                    "selected_option": None
                })
        
        try:
            response = requests.post(
                f"{self.api_url}/resolve",
                json={
                    "session_id": self.session_id,
                    "answers": answers
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log_test("Resolve Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify response structure
            required_fields = ["session_id", "resolution", "confidence_score", "can_proceed"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_test("Resolve Endpoint", False, f"Missing fields: {missing_fields}")
                return {}
            
            # Check if confidence improved
            new_confidence = data.get("confidence_score", 0)
            old_confidence = analysis_data.get("confidence_score", 0)
            if new_confidence > old_confidence:
                self.log_test("Confidence Improvement", True, f"Confidence increased from {old_confidence}% to {new_confidence}%")
            else:
                self.log_test("Confidence Improvement", False, f"Confidence did not improve: {old_confidence}% -> {new_confidence}%")
            
            self.log_test("Resolve Endpoint", True, f"Processed {len(answers)} answers, confidence: {new_confidence}%")
            return data
            
        except Exception as e:
            self.log_test("Resolve Endpoint", False, str(e))
            return {}

    def test_generate_spec_endpoint(self, can_proceed: bool) -> Dict[str, Any]:
        """Test the /generate-spec endpoint"""
        if not self.session_id:
            self.log_test("Generate Spec Endpoint", False, "No session available")
            return {}
        
        try:
            response = requests.post(
                f"{self.api_url}/generate-spec",
                json={"session_id": self.session_id},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if not can_proceed:
                # Should fail if confidence is too low
                if response.status_code == 400:
                    self.log_test("Generate Spec Endpoint (Low Confidence)", True, "Correctly rejected low confidence spec generation")
                    return {}
                else:
                    self.log_test("Generate Spec Endpoint (Low Confidence)", False, f"Should have rejected but got {response.status_code}")
                    return {}
            
            if response.status_code != 200:
                self.log_test("Generate Spec Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify specification structure
            if "specification" not in data:
                self.log_test("Generate Spec Endpoint", False, "No specification in response")
                return {}
            
            spec = data["specification"]
            if isinstance(spec, dict) and len(spec) > 0:
                self.log_test("Generate Spec Endpoint", True, "Generated formal specification")
            else:
                self.log_test("Generate Spec Endpoint", False, "Invalid specification format")
            
            return data
            
        except Exception as e:
            self.log_test("Generate Spec Endpoint", False, str(e))
            return {}

    def test_session_retrieval(self) -> bool:
        """Test session retrieval endpoints"""
        if not self.session_id:
            self.log_test("Session Retrieval", False, "No session to retrieve")
            return False
        
        try:
            # Test individual session retrieval
            response = requests.get(f"{self.api_url}/session/{self.session_id}", timeout=10)
            if response.status_code == 200:
                session_data = response.json()
                if session_data.get("session_id") == self.session_id:
                    self.log_test("Individual Session Retrieval", True, "Session retrieved successfully")
                else:
                    self.log_test("Individual Session Retrieval", False, "Session ID mismatch")
            else:
                self.log_test("Individual Session Retrieval", False, f"HTTP {response.status_code}")
            
            # Test sessions list
            response = requests.get(f"{self.api_url}/sessions", timeout=10)
            if response.status_code == 200:
                sessions_data = response.json()
                if "sessions" in sessions_data and isinstance(sessions_data["sessions"], list):
                    self.log_test("Sessions List", True, f"Retrieved {len(sessions_data['sessions'])} sessions")
                else:
                    self.log_test("Sessions List", False, "Invalid sessions list format")
            else:
                self.log_test("Sessions List", False, f"HTTP {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Session Retrieval", False, str(e))
            return False

    def test_genesis_project_init(self) -> Dict[str, Any]:
        """Test POST /api/genesis/project/init - Initialize orchestrator with agents"""
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
            
            if response.status_code != 200:
                self.log_test("Genesis Project Init", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify required fields
            required_fields = ["orchestrator_id", "primary_kernel_id", "agents", "status"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_test("Genesis Project Init", False, f"Missing fields: {missing_fields}")
                return {}
            
            # Store IDs for subsequent tests
            self.orchestrator_id = data["orchestrator_id"]
            self.project_id = data["orchestrator_id"]  # Using orchestrator_id as project_id
            
            # Verify agents are initialized
            agents = data.get("agents", [])
            if len(agents) >= 6:  # Should have 6 agent tiers
                agent_tiers = [agent.get("tier") for agent in agents]
                expected_tiers = ["commander", "architect", "builder", "validator", "guardian", "executor"]
                if all(tier in agent_tiers for tier in expected_tiers):
                    self.log_test("Agent Hierarchy Initialized", True, f"Found {len(agents)} agents with all tiers")
                else:
                    self.log_test("Agent Hierarchy Initialized", False, f"Missing tiers. Found: {agent_tiers}")
            else:
                self.log_test("Agent Hierarchy Initialized", False, f"Expected 6+ agents, got {len(agents)}")
            
            self.log_test("Genesis Project Init", True, f"Project {self.project_id} initialized with {len(agents)} agents")
            return data
            
        except Exception as e:
            self.log_test("Genesis Project Init", False, str(e))
            return {}

    def test_quality_assessment(self) -> Dict[str, Any]:
        """Test POST /api/genesis/quality/assess - 8-dimensional quality assessment"""
        test_artifact = {
            "name": "Test System",
            "components": ["auth", "api", "database"],
            "security": {"authentication": "oauth2", "encryption": "aes256"},
            "performance_requirements": {"latency": "100ms", "throughput": "1000rps"}
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
            
            if response.status_code != 200:
                self.log_test("Quality Assessment", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify 8-dimensional assessment
            required_fields = ["aggregate_score", "passed", "dimension_scores", "improvement_priority"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_test("Quality Assessment", False, f"Missing fields: {missing_fields}")
                return {}
            
            # Check 8 dimensions
            dimensions = data.get("dimension_scores", [])
            expected_dimensions = [
                "completeness", "coherence", "correctness", "security", 
                "performance", "scalability", "maintainability", "compliance"
            ]
            
            dimension_names = [d.get("dimension") for d in dimensions]
            if len(dimensions) == 8 and all(dim in dimension_names for dim in expected_dimensions):
                self.log_test("8-Dimensional Scoring", True, f"All 8 dimensions assessed: {dimension_names}")
            else:
                self.log_test("8-Dimensional Scoring", False, f"Expected 8 dimensions, got {len(dimensions)}: {dimension_names}")
            
            # Verify aggregate score
            score = data.get("aggregate_score", 0)
            if 0 <= score <= 100:
                self.log_test("Quality Score Range", True, f"Score: {score}%")
            else:
                self.log_test("Quality Score Range", False, f"Invalid score: {score}")
            
            self.log_test("Quality Assessment", True, f"8D assessment complete, score: {score}%")
            return data
            
        except Exception as e:
            self.log_test("Quality Assessment", False, str(e))
            return {}

    def test_ouroboros_execution(self) -> Dict[str, Any]:
        """Test POST /api/genesis/ouroboros/execute - Improvement loop until 99% convergence"""
        if not self.project_id:
            self.log_test("Ouroboros Execution", False, "No project initialized")
            return {}
        
        test_artifact = {
            "name": "Test System",
            "components": ["auth", "api", "database"],
            "validated": True,
            "documentation": "Complete system documentation"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/genesis/ouroboros/execute",
                json={
                    "project_id": self.project_id,
                    "artifact": test_artifact,
                    "stage": "validation"
                },
                headers={"Content-Type": "application/json"},
                timeout=60  # Longer timeout for iterative improvement
            )
            
            if response.status_code != 200:
                self.log_test("Ouroboros Execution", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify Ouroboros result structure
            required_fields = ["status", "final_score", "iterations", "artifact", "history"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_test("Ouroboros Execution", False, f"Missing fields: {missing_fields}")
                return {}
            
            # Check convergence behavior
            status = data.get("status")
            final_score = data.get("final_score", 0)
            iterations = data.get("iterations", 0)
            
            if status in ["CONVERGED", "MAX_ITERATIONS", "DRIFT_ALERT"]:
                self.log_test("Ouroboros Status", True, f"Status: {status}, Score: {final_score}%, Iterations: {iterations}")
            else:
                self.log_test("Ouroboros Status", False, f"Invalid status: {status}")
            
            # Check if improvement occurred
            if iterations > 0:
                self.log_test("Iterative Improvement", True, f"Completed {iterations} improvement iterations")
            else:
                self.log_test("Iterative Improvement", False, "No iterations performed")
            
            self.log_test("Ouroboros Execution", True, f"Loop executed: {status} after {iterations} iterations")
            return data
            
        except Exception as e:
            self.log_test("Ouroboros Execution", False, str(e))
            return {}

    def test_compliance_audit(self) -> Dict[str, Any]:
        """Test POST /api/governance/compliance/audit - Compliance checking"""
        test_artifact = {
            "security": {
                "authentication": "oauth2",
                "authorization": "rbac",
                "encryption": {"at_rest": "aes256", "in_transit": "tls13"}
            },
            "features": {
                "audit_log": True,
                "consent_management": True
            },
            "policies": {
                "data_retention": "7 years"
            }
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
            
            if response.status_code != 200:
                self.log_test("Compliance Audit", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify compliance audit structure
            required_fields = ["compliance_score", "total_checks", "passed", "failed", "results"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_test("Compliance Audit", False, f"Missing fields: {missing_fields}")
                return {}
            
            # Check compliance categories
            results = data.get("results", [])
            categories_found = set(r.get("category") for r in results)
            if "security" in categories_found and "data_privacy" in categories_found:
                self.log_test("Compliance Categories", True, f"Categories audited: {list(categories_found)}")
            else:
                self.log_test("Compliance Categories", False, f"Expected security & data_privacy, got: {list(categories_found)}")
            
            # Check compliance score
            score = data.get("compliance_score", 0)
            if 0 <= score <= 100:
                self.log_test("Compliance Score", True, f"Score: {score}%")
            else:
                self.log_test("Compliance Score", False, f"Invalid score: {score}")
            
            self.log_test("Compliance Audit", True, f"Audit complete: {score}% compliance across {len(categories_found)} categories")
            return data
            
        except Exception as e:
            self.log_test("Compliance Audit", False, str(e))
            return {}

    def test_orchestrator_agents(self) -> Dict[str, Any]:
        """Test GET /api/orchestrator/agents - List all agents with tiers"""
        try:
            response = requests.get(
                f"{self.api_url}/orchestrator/agents",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Orchestrator Agents", False, f"HTTP {response.status_code}: {response.text}")
                return {}
            
            data = response.json()
            
            # Verify agents structure
            if "agents" not in data:
                self.log_test("Orchestrator Agents", False, "No agents field in response")
                return {}
            
            agents = data.get("agents", [])
            if len(agents) == 0:
                self.log_test("Orchestrator Agents", False, "No agents found")
                return {}
            
            # Check agent tiers
            agent_tiers = [agent.get("tier") for agent in agents]
            expected_tiers = ["commander", "architect", "builder", "validator", "guardian", "executor"]
            found_tiers = [tier for tier in expected_tiers if tier in agent_tiers]
            
            if len(found_tiers) >= 6:
                self.log_test("Agent Tiers", True, f"Found all tiers: {found_tiers}")
            else:
                self.log_test("Agent Tiers", False, f"Missing tiers. Found: {found_tiers}")
            
            # Check agent structure
            first_agent = agents[0]
            required_agent_fields = ["agent_id", "name", "tier", "status", "capabilities"]
            missing_agent_fields = [f for f in required_agent_fields if f not in first_agent]
            if not missing_agent_fields:
                self.log_test("Agent Structure", True, "Agents have all required fields")
            else:
                self.log_test("Agent Structure", False, f"Missing fields: {missing_agent_fields}")
            
            self.log_test("Orchestrator Agents", True, f"Listed {len(agents)} agents across {len(found_tiers)} tiers")
            return data
            
        except Exception as e:
            self.log_test("Orchestrator Agents", False, str(e))
            return {}

    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite for Genesis Pipeline v2.0"""
        print("🚀 Starting Sovereign Genesis Platform v2.0 API Tests")
        print(f"🔗 Testing against: {self.api_url}")
        print("=" * 60)
        
        # Test 1: Basic connectivity and v2.0 features
        if not self.test_api_health():
            print("❌ API not accessible, stopping tests")
            return self.get_summary()
        
        # Test 2: Genesis Project Initialization
        genesis_data = self.test_genesis_project_init()
        if not genesis_data:
            print("❌ Genesis project initialization failed")
        
        # Test 3: Quality Assessment (8-dimensional)
        quality_data = self.test_quality_assessment()
        
        # Test 4: Ouroboros Loop Execution
        ouroboros_data = self.test_ouroboros_execution()
        
        # Test 5: Compliance Audit
        compliance_data = self.test_compliance_audit()
        
        # Test 6: Orchestrator Agents
        agents_data = self.test_orchestrator_agents()
        
        # Test 7: Core Socratic Engine (backward compatibility)
        analysis_data = self.test_analyze_endpoint()
        if not analysis_data:
            print("❌ Socratic Engine analysis failed")
        else:
            # Test 8: Resolution process
            resolution_data = self.test_resolve_endpoint(analysis_data)
            
            # Test 9: Spec generation (should fail with low confidence)
            can_proceed = resolution_data.get("can_proceed", False) if resolution_data else False
            self.test_generate_spec_endpoint(can_proceed)
        
        # Test 10: Session management
        self.test_session_retrieval()
        
        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        summary = {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": round(success_rate, 1),
            "session_id": self.session_id,
            "test_results": self.test_results
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        print(f"🆔 Session ID: {self.session_id}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! SGP backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return summary

def main():
    """Main test execution"""
    tester = SGPAPITester()
    summary = tester.run_full_test_suite()
    
    # Return appropriate exit code
    return 0 if summary["failed_tests"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())