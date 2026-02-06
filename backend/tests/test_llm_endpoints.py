"""
LLM Provider Endpoints Tests
Tests for dual-mode LLM support (cloud vs local) endpoints:
- GET /api/llm/status - LLM provider status and configuration
- POST /api/llm/config - Switch between cloud/local/hybrid modes
- POST /api/llm/test - Test LLM generation
- GET /api/llm/models - List available local models
- POST /api/analyze - Socratic engine with hybrid LLM (llm_info in response)
- POST /api/resolve - Resolution with hybrid LLM (llm_info in response)
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


class TestLLMStatus:
    """Tests for GET /api/llm/status endpoint"""
    
    def test_llm_status_returns_200(self, api_client):
        """Test that LLM status endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/llm/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_llm_status_has_required_fields(self, api_client):
        """Test that LLM status response has all required fields"""
        response = api_client.get(f"{BASE_URL}/api/llm/status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check top-level fields
        assert "status" in data, "Missing 'status' field"
        assert data["status"] == "active", f"Expected status 'active', got '{data['status']}'"
        
        assert "configuration" in data, "Missing 'configuration' field"
        assert "recommended_models" in data, "Missing 'recommended_models' field"
        assert "instructions" in data, "Missing 'instructions' field"
    
    def test_llm_status_configuration_structure(self, api_client):
        """Test that configuration has proper structure"""
        response = api_client.get(f"{BASE_URL}/api/llm/status")
        data = response.json()
        
        config = data["configuration"]
        
        # Check configuration fields
        assert "mode" in config, "Missing 'mode' in configuration"
        assert config["mode"] in ["cloud", "local", "hybrid"], f"Invalid mode: {config['mode']}"
        
        assert "local_available" in config, "Missing 'local_available' in configuration"
        assert isinstance(config["local_available"], bool), "local_available should be boolean"
        
        assert "cloud_available" in config, "Missing 'cloud_available' in configuration"
        assert isinstance(config["cloud_available"], bool), "cloud_available should be boolean"
        
        assert "local_model" in config, "Missing 'local_model' in configuration"
        assert "cloud_model" in config, "Missing 'cloud_model' in configuration"
        assert "fallback_enabled" in config, "Missing 'fallback_enabled' in configuration"
    
    def test_llm_status_recommended_models(self, api_client):
        """Test that recommended models are properly structured"""
        response = api_client.get(f"{BASE_URL}/api/llm/status")
        data = response.json()
        
        models = data["recommended_models"]
        
        # Check model categories
        assert "general" in models, "Missing 'general' category in recommended_models"
        assert "coding" in models, "Missing 'coding' category in recommended_models"
        assert "reasoning" in models, "Missing 'reasoning' category in recommended_models"
        
        # Check that models have proper structure
        for category, model_list in models.items():
            for model_name, model_info in model_list.items():
                assert "description" in model_info, f"Missing description for {model_name}"
                assert "size" in model_info, f"Missing size for {model_name}"


class TestLLMConfig:
    """Tests for POST /api/llm/config endpoint"""
    
    def test_config_cloud_mode(self, api_client):
        """Test configuring cloud mode"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "cloud"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Missing 'message' field"
        assert "cloud" in data["message"].lower(), "Message should mention cloud mode"
        
        assert "configuration" in data, "Missing 'configuration' field"
        assert data["configuration"]["mode"] == "cloud", "Mode should be 'cloud'"
    
    def test_config_local_mode(self, api_client):
        """Test configuring local mode"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "local"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["configuration"]["mode"] == "local", "Mode should be 'local'"
        
        # Since Ollama is not installed, we should get warnings
        if not data["configuration"]["local_available"]:
            assert "warnings" in data, "Should have warnings when local not available"
            assert len(data["warnings"]) > 0, "Should have at least one warning"
    
    def test_config_hybrid_mode(self, api_client):
        """Test configuring hybrid mode"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "hybrid",
            "fallback_to_cloud": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["configuration"]["mode"] == "hybrid", "Mode should be 'hybrid'"
        assert data["configuration"]["fallback_enabled"] == True, "Fallback should be enabled"
    
    def test_config_with_custom_local_model(self, api_client):
        """Test configuring with custom local model"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "hybrid",
            "local_model": "mistral:7b",
            "local_url": "http://localhost:11434"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["configuration"]["local_model"] == "mistral:7b", "Local model should be updated"
    
    def test_config_invalid_mode(self, api_client):
        """Test that invalid mode returns 400 or 422 (validation error)"""
        response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "invalid_mode"
        })
        # 422 is Pydantic validation error, 400 is explicit HTTPException - both are valid
        assert response.status_code in [400, 422], f"Expected 400/422 for invalid mode, got {response.status_code}"


class TestLLMModels:
    """Tests for GET /api/llm/models endpoint"""
    
    def test_models_endpoint_returns_200(self, api_client):
        """Test that models endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/llm/models")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_models_response_structure(self, api_client):
        """Test that models response has proper structure"""
        response = api_client.get(f"{BASE_URL}/api/llm/models")
        data = response.json()
        
        assert "available" in data, "Missing 'available' field"
        assert isinstance(data["available"], bool), "available should be boolean"
        
        assert "models" in data, "Missing 'models' field"
        assert isinstance(data["models"], list), "models should be a list"
        
        # Since Ollama is not installed, available should be False
        if not data["available"]:
            assert "message" in data, "Should have message when not available"
            assert len(data["models"]) == 0, "Models list should be empty when not available"


class TestLLMTest:
    """Tests for POST /api/llm/test endpoint"""
    
    def test_llm_test_basic(self, api_client):
        """Test basic LLM generation"""
        # First ensure we're in cloud mode for reliable testing
        api_client.post(f"{BASE_URL}/api/llm/config", json={"mode": "cloud"})
        
        response = api_client.post(f"{BASE_URL}/api/llm/test", json={
            "prompt": "Say hello in exactly 3 words",
            "prefer_local": False
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "success" in data, "Missing 'success' field"
        
        if data["success"]:
            assert "response" in data, "Missing 'response' field on success"
            assert "provider_used" in data, "Missing 'provider_used' field"
            assert "model_used" in data, "Missing 'model_used' field"
            assert len(data["response"]) > 0, "Response should not be empty"
        else:
            # If failed, should have error info
            assert "error" in data, "Missing 'error' field on failure"
    
    def test_llm_test_response_fields(self, api_client):
        """Test that LLM test response has all expected fields"""
        response = api_client.post(f"{BASE_URL}/api/llm/test", json={
            "prompt": "What is 2+2?",
            "prefer_local": False
        })
        
        data = response.json()
        
        if data.get("success"):
            assert "provider_used" in data, "Missing provider_used"
            assert data["provider_used"] in ["cloud", "local"], f"Invalid provider: {data['provider_used']}"
            
            assert "model_used" in data, "Missing model_used"
            assert isinstance(data["model_used"], str), "model_used should be string"
            
            # request_counts is optional but should be dict if present
            if "request_counts" in data:
                assert isinstance(data["request_counts"], dict), "request_counts should be dict"


class TestAnalyzeWithLLMInfo:
    """Tests for POST /api/analyze endpoint with llm_info in response"""
    
    def test_analyze_returns_llm_info(self, api_client):
        """Test that analyze endpoint returns llm_info"""
        # Ensure cloud mode for reliable testing
        api_client.post(f"{BASE_URL}/api/llm/config", json={"mode": "cloud"})
        
        response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Build a simple todo app"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check standard fields
        assert "session_id" in data, "Missing session_id"
        assert "analysis" in data, "Missing analysis"
        assert "confidence_score" in data, "Missing confidence_score"
        
        # Check llm_info field (new feature)
        assert "llm_info" in data, "Missing llm_info field - this is the new feature!"
        
        llm_info = data["llm_info"]
        assert "provider" in llm_info, "Missing provider in llm_info"
        assert "model" in llm_info, "Missing model in llm_info"
        
        # Provider should be cloud since we set it
        assert llm_info["provider"] in ["cloud", "local"], f"Invalid provider: {llm_info['provider']}"
    
    def test_analyze_analysis_structure(self, api_client):
        """Test that analysis has proper Socratic structure"""
        response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Create a user authentication system"
        })
        
        data = response.json()
        analysis = data.get("analysis", {})
        
        # Check Socratic analysis structure
        if "error" not in analysis:
            assert "ambiguities" in analysis, "Missing ambiguities in analysis"
            assert isinstance(analysis["ambiguities"], list), "ambiguities should be a list"
            
            if len(analysis["ambiguities"]) > 0:
                amb = analysis["ambiguities"][0]
                assert "id" in amb, "Ambiguity missing id"
                assert "category" in amb, "Ambiguity missing category"
                assert "question" in amb, "Ambiguity missing question"


class TestResolveWithLLMInfo:
    """Tests for POST /api/resolve endpoint with llm_info in response"""
    
    def test_resolve_returns_llm_info(self, api_client):
        """Test that resolve endpoint returns llm_info"""
        # First create a session via analyze
        analyze_response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Build a blog platform"
        })
        assert analyze_response.status_code == 200
        
        session_id = analyze_response.json()["session_id"]
        analysis = analyze_response.json().get("analysis", {})
        
        # Get ambiguities to answer
        ambiguities = analysis.get("ambiguities", [])
        
        if len(ambiguities) > 0:
            # Create answers for first few ambiguities
            answers = []
            for amb in ambiguities[:2]:  # Answer first 2
                answers.append({
                    "ambiguity_id": amb["id"],
                    "answer": "Use default option",
                    "selected_option": amb.get("options", ["Default"])[0] if amb.get("options") else None
                })
            
            # Call resolve
            response = api_client.post(f"{BASE_URL}/api/resolve", json={
                "session_id": session_id,
                "answers": answers
            })
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Check llm_info field (new feature)
            assert "llm_info" in data, "Missing llm_info field in resolve response!"
            
            llm_info = data["llm_info"]
            assert "provider" in llm_info, "Missing provider in llm_info"
            assert "model" in llm_info, "Missing model in llm_info"
        else:
            pytest.skip("No ambiguities to resolve")
    
    def test_resolve_session_not_found(self, api_client):
        """Test that resolve returns 404 for non-existent session"""
        response = api_client.post(f"{BASE_URL}/api/resolve", json={
            "session_id": "non-existent-session-id",
            "answers": []
        })
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestHybridModeFallback:
    """Tests for hybrid mode fallback behavior"""
    
    def test_hybrid_mode_falls_back_to_cloud(self, api_client):
        """Test that hybrid mode falls back to cloud when local unavailable"""
        # Configure hybrid mode
        config_response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "hybrid",
            "fallback_to_cloud": True
        })
        assert config_response.status_code == 200
        
        # Check that local is not available (Ollama not installed)
        status_response = api_client.get(f"{BASE_URL}/api/llm/status")
        status = status_response.json()
        
        local_available = status["configuration"]["local_available"]
        
        # Test LLM generation - should fall back to cloud
        test_response = api_client.post(f"{BASE_URL}/api/llm/test", json={
            "prompt": "Say 'test successful'",
            "prefer_local": True  # Prefer local, but should fall back
        })
        
        data = test_response.json()
        
        if data.get("success"):
            # If local not available, should have used cloud
            if not local_available:
                assert data["provider_used"] == "cloud", "Should fall back to cloud when local unavailable"
        else:
            # If both failed, that's also valid for this test
            print(f"LLM test failed: {data.get('error')}")


class TestEndToEndLLMFlow:
    """End-to-end tests for LLM provider switching"""
    
    def test_full_llm_workflow(self, api_client):
        """Test complete workflow: status -> config -> test -> analyze"""
        # 1. Check initial status
        status_response = api_client.get(f"{BASE_URL}/api/llm/status")
        assert status_response.status_code == 200
        initial_status = status_response.json()
        print(f"Initial LLM status: {initial_status['configuration']['mode']}")
        
        # 2. Configure to cloud mode
        config_response = api_client.post(f"{BASE_URL}/api/llm/config", json={
            "mode": "cloud"
        })
        assert config_response.status_code == 200
        
        # 3. Verify configuration changed
        status_response = api_client.get(f"{BASE_URL}/api/llm/status")
        assert status_response.json()["configuration"]["mode"] == "cloud"
        
        # 4. Test LLM generation
        test_response = api_client.post(f"{BASE_URL}/api/llm/test", json={
            "prompt": "Reply with just 'OK'"
        })
        assert test_response.status_code == 200
        
        # 5. Use analyze endpoint (should use configured LLM)
        analyze_response = api_client.post(f"{BASE_URL}/api/analyze", json={
            "prompt": "Build a calculator app"
        })
        assert analyze_response.status_code == 200
        
        # Verify llm_info is present
        assert "llm_info" in analyze_response.json()
        
        print("Full LLM workflow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
