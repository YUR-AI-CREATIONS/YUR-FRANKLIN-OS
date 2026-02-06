#!/usr/bin/env python3
"""
Sovereign Genesis Platform (SGP) Backend API Testing
Tests the Socratic Pre-Prompt Engine and Neural-Symbolic reasoning endpoints
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

class SGPAPITester:
    def __init__(self, base_url="https://app-cloner-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
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
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" - {data.get('message', 'No message')}"
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
                timeout=30
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
                timeout=30
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
                timeout=30
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

    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🚀 Starting Sovereign Genesis Platform API Tests")
        print(f"🔗 Testing against: {self.api_url}")
        print("=" * 60)
        
        # Test 1: Basic connectivity
        if not self.test_api_health():
            print("❌ API not accessible, stopping tests")
            return self.get_summary()
        
        # Test 2: Core Socratic Engine
        analysis_data = self.test_analyze_endpoint()
        if not analysis_data:
            print("❌ Analysis failed, stopping tests")
            return self.get_summary()
        
        # Test 3: Resolution process
        resolution_data = self.test_resolve_endpoint(analysis_data)
        
        # Test 4: Spec generation (should fail with low confidence)
        can_proceed = resolution_data.get("can_proceed", False) if resolution_data else False
        self.test_generate_spec_endpoint(can_proceed)
        
        # Test 5: Session management
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