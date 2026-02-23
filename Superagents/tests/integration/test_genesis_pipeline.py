import requests
import unittest
import logging
import json

# Configuration
API_BASE = "http://localhost:8000/api/v1" # Mock Target
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SDET_Audit")

class TestGenesisPipeline(unittest.TestCase):
    """
    Rigorous Integration Suite for the Cognitive Engine.
    Verifies: Connectivity, Schema Integrity, Business Logic, State Flow.
    """
    
    def setUp(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.project_id = None

    def log_test(self, name, success, details=""):
        status = "✅" if success else "❌"
        logger.info(f"{status} [{name}] {details}")

    def test_01_api_root_integrity(self):
        """Verify API versioning and module availability."""
        try:
            resp = self.session.get(f"{API_BASE}/health", timeout=5)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            
            # Schema Validation
            self.assertIn("version", data)
            self.assertIn("modules", data)
            
            # Business Logic: Ensure core modules are active
            required_modules = ["oracle", "cipher", "flow"]
            active_modules = data.get("modules", [])
            missing = [m for m in required_modules if m not in active_modules]
            self.assertEqual(len(missing), 0, f"Missing modules: {missing}")
            
            self.log_test("API Root Integrity", True)
        except Exception as e:
            self.log_test("API Root Integrity", False, str(e))
            raise

    def test_02_genesis_project_init(self):
        """Test state creation and capture ID for workflow."""
        payload = {"name": "Test_Genesis_Protocol", "tier": "cognitive_alpha"}
        try:
            resp = self.session.post(f"{API_BASE}/projects", json=payload, timeout=10)
            self.assertEqual(resp.status_code, 201)
            data = resp.json()
            
            # State Capture
            TestGenesisPipeline.project_id = data.get("id")
            self.assertIsNotNone(TestGenesisPipeline.project_id)
            
            self.log_test("Genesis Project Init", True, f"ID: {TestGenesisPipeline.project_id}")
        except Exception as e:
            self.log_test("Genesis Project Init", False, str(e))
            raise

    def test_03_orchestrator_agents(self):
        """Verify Agentic Hierarchy exists."""
        try:
            resp = self.session.get(f"{API_BASE}/agents", timeout=10)
            self.assertEqual(resp.status_code, 200)
            agents = resp.json()
            
            # Deep Inspection
            roles = [a.get("role") for a in agents]
            self.assertIn("Oracle", roles)
            self.assertIn("Chat_1", roles)
            
            self.log_test("Orchestrator Agents", True, f"Active: {roles}")
        except Exception as e:
            self.log_test("Orchestrator Agents", False, str(e))
            raise

if __name__ == "__main__":
    unittest.main()
