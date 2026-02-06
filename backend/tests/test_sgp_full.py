"""
Sovereign Genesis Platform - Full End-to-End Tests
Tests for all major endpoints:
- LLM Provider endpoints (status, config, test, models)
- Socratic Engine (analyze, resolve)
- Genesis Pipeline (project/init, quality/assess)
- Tech Stack (catalog)
- Build Engine (generate)
"""

import pytest
import requests
import os
import uuid

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestAPIRoot:
    """Tests for API root endpoint"""
    
    def test_api_root_returns_200(self, api_client):
        """Test that API root returns 200"""
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        
    def test_api_root_has_version(self, api_client):
        """Test that API root returns version info"""
        response = api_client.get(f"{BASE_URL}/api/")
        data = response.json()
        
        assert "version" in data
        assert data["version"] == "2.0.0"
        assert "modules" in data
        assert len(data["modules"]) >= 6


class TestLLMStatus:
    """Tests for GET /api/llm/status endpoint"""
    
    def test_llm_status_returns_200(self, api_client):
        """Test that LLM status endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/llm/status")
        assert response.status_code == 200
    
    def test_llm_status_has_configuration(self, api_client):
        """Test that LLM status has configuration"""
        response = api_client.get(f"{BASE_URL}/api/llm/status")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "active"
        assert "configuration" in data
        
        config = data["configuration"]
        assert "mode" in config
        assert config["mode"] in ["cloud", "local", "hybrid"]
        assert "local_available" in config
        assert "cloud_available" in config


class TestLLMConfig:
    """Tests for POST /api/llm/config endpoint"""
    
    def test_config_cloud_mode(self, api_client):
        """Test configuring cloud mode"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "cloud"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["configuration"]["mode"] == "cloud"
    
    def test_config_hybrid_mode(self, api_client):
        """Test configuring hybrid mode"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "hybrid",
            "fallback_to_cloud": True
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["configuration"]["mode"] == "hybrid"
        assert data["configuration"]["fallback_enabled"] == True
    
    def test_config_local_mode_with_warnings(self, api_client):
        """Test configuring local mode shows warnings when Ollama not available"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "local"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["configuration"]["mode"] == "local"
        
        # Should have warnings if local not available
        if not data["configuration"]["local_available"]:
            assert "warnings" in data
            assert len(data["warnings"]) > 0
        
        # Restore cloud mode for subsequent tests
        api_client.post(f"{BASE_URL}/api/llm/config", json={"mode": "cloud"})


class TestAnalyzeEndpoint:
    """Tests for POST /api/analyze endpoint"""
    
    def test_analyze_returns_session_id(self, api_client):
        """Test that analyze returns session_id"""
        response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Build a simple calculator"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
    
    def test_analyze_returns_llm_info(self, api_client):
        """Test that analyze returns llm_info"""
        response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Create a blog platform"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "llm_info" in data
        assert "provider" in data["llm_info"]
        assert "model" in data["llm_info"]
    
    def test_analyze_returns_ambiguities(self, api_client):
        """Test that analyze returns ambiguities"""
        response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Build a todo app"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis" in data
        
        analysis = data["analysis"]
        if "error" not in analysis:
            assert "ambiguities" in analysis
            assert isinstance(analysis["ambiguities"], list)
            
            if len(analysis["ambiguities"]) > 0:
                amb = analysis["ambiguities"][0]
                assert "id" in amb
                assert "category" in amb
                assert "question" in amb
                assert "priority" in amb
    
    def test_analyze_returns_confidence_score(self, api_client):
        """Test that analyze returns confidence score"""
        response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Build a REST API"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "confidence_score" in data
        assert isinstance(data["confidence_score"], (int, float))
        assert "can_proceed" in data
        assert isinstance(data["can_proceed"], bool)


class TestGenesisProjectInit:
    """Tests for POST /api/genesis/project/init endpoint"""
    
    def test_project_init_returns_orchestrator_id(self, api_client):
        """Test that project init returns orchestrator_id"""
        response = api_client.post(f"{BASE_URL}/api/genesis/project/init", json={
            "name": "TEST_Project",
            "description": "Test project for testing"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "orchestrator_id" in data
        assert len(data["orchestrator_id"]) > 0
    
    def test_project_init_returns_agents(self, api_client):
        """Test that project init returns agents"""
        response = api_client.post(f"{BASE_URL}/api/genesis/project/init", json={
            "name": "TEST_AgentProject",
            "description": "Test project with agents"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) >= 4  # At least 4 agent tiers
        
        # Check agent structure
        agent = data["agents"][0]
        assert "id" in agent
        assert "name" in agent
        assert "tier" in agent
    
    def test_project_init_returns_primary_kernel(self, api_client):
        """Test that project init returns primary kernel"""
        response = api_client.post(f"{BASE_URL}/api/genesis/project/init", json={
            "name": "TEST_KernelProject",
            "description": "Test project with kernel"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "primary_kernel_id" in data
        assert len(data["primary_kernel_id"]) > 0


class TestQualityAssess:
    """Tests for POST /api/genesis/quality/assess endpoint"""
    
    def test_quality_assess_returns_scores(self, api_client):
        """Test that quality assess returns dimension scores"""
        response = api_client.post(f"{BASE_URL}/api/genesis/quality/assess", json={
            "artifact": {
                "name": "TestArtifact",
                "type": "specification",
                "requirements": ["req1", "req2"]
            },
            "stage": "specification"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "aggregate_score" in data
        assert isinstance(data["aggregate_score"], (int, float))
        assert "passed" in data
        assert isinstance(data["passed"], bool)
    
    def test_quality_assess_returns_dimensions(self, api_client):
        """Test that quality assess returns dimension details"""
        response = api_client.post(f"{BASE_URL}/api/genesis/quality/assess", json={
            "artifact": {"name": "Test", "type": "spec"},
            "stage": "specification"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "dimension_scores" in data
        assert isinstance(data["dimension_scores"], list)
        
        if len(data["dimension_scores"]) > 0:
            dim = data["dimension_scores"][0]
            assert "dimension" in dim
            assert "score" in dim
            assert "weight" in dim


class TestStackCatalog:
    """Tests for GET /api/stack/catalog endpoint"""
    
    def test_stack_catalog_returns_200(self, api_client):
        """Test that stack catalog returns 200"""
        response = api_client.get(f"{BASE_URL}/api/stack/catalog")
        assert response.status_code == 200
    
    def test_stack_catalog_has_categories(self, api_client):
        """Test that stack catalog has technology categories"""
        response = api_client.get(f"{BASE_URL}/api/stack/catalog")
        data = response.json()
        
        # Should have multiple categories
        assert len(data) > 0
        
        # Check for common categories
        expected_categories = ["cloud_provider", "container_orchestration", "database"]
        for cat in expected_categories:
            if cat in data:
                assert isinstance(data[cat], list)
                if len(data[cat]) > 0:
                    tech = data[cat][0]
                    assert "id" in tech
                    assert "name" in tech


class TestBuildGenerate:
    """Tests for POST /api/build/generate endpoint"""
    
    def test_build_generate_returns_artifacts(self, api_client):
        """Test that build generate returns artifacts"""
        response = api_client.post(f"{BASE_URL}/api/build/generate", json={
            "project_id": f"TEST_{uuid.uuid4().hex[:8]}",
            "project_name": "TestBuildApp",
            "specification": {
                "name": "TestBuildApp",
                "features": ["auth", "crud"]
            },
            "tech_stack": {
                "frontend": "react",
                "backend": "fastapi"
            }
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "build_id" in data
        assert "project_name" in data
        assert "total_artifacts" in data
        assert data["total_artifacts"] > 0
    
    def test_build_generate_returns_artifact_breakdown(self, api_client):
        """Test that build generate returns artifact breakdown by language"""
        response = api_client.post(f"{BASE_URL}/api/build/generate", json={
            "project_id": f"TEST_{uuid.uuid4().hex[:8]}",
            "project_name": "TestBreakdownApp",
            "specification": {"name": "TestBreakdownApp"},
            "tech_stack": {"frontend": "react", "backend": "fastapi"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "artifacts_by_language" in data
        assert isinstance(data["artifacts_by_language"], dict)


class TestEndToEndFlow:
    """End-to-end tests for complete workflow"""
    
    def test_full_socratic_to_genesis_flow(self, api_client):
        """Test complete flow: analyze -> project init -> quality assess"""
        # 1. Analyze prompt
        analyze_response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Build a task management system"
        })
        assert analyze_response.status_code == 200
        
        analyze_data = analyze_response.json()
        assert "session_id" in analyze_data
        assert "llm_info" in analyze_data
        
        # 2. Initialize Genesis project
        project_response = api_client.post(f"{BASE_URL}/api/genesis/project/init", json={
            "name": "TEST_E2E_TaskManager",
            "description": "End-to-end test project"
        })
        assert project_response.status_code == 200
        
        project_data = project_response.json()
        assert "orchestrator_id" in project_data
        
        # 3. Run quality assessment
        quality_response = api_client.post(f"{BASE_URL}/api/genesis/quality/assess", json={
            "artifact": {
                "name": "TaskManager",
                "type": "specification",
                "analysis": analyze_data.get("analysis", {})
            },
            "stage": "specification"
        })
        assert quality_response.status_code == 200
        
        quality_data = quality_response.json()
        assert "aggregate_score" in quality_data
        
        print(f"E2E Flow completed: session={analyze_data['session_id'][:8]}, "
              f"project={project_data['orchestrator_id'][:8]}, "
              f"quality_score={quality_data['aggregate_score']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
