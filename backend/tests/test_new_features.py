"""
Test suite for SGP v2.0 New Features:
- Prompt Optimization (quick and LLM modes)
- Enhanced Build Engine (CRUD, Auth, Tests)
- ZIP Download
- Marketing Content Generation
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://code-genesis-14.preview.emergentagent.com').rstrip('/')


class TestPromptOptimization:
    """Test prompt optimization endpoints"""
    
    def test_quick_optimize_basic(self):
        """Test quick optimization with basic prompt"""
        response = requests.post(
            f"{BASE_URL}/api/prompt/optimize",
            json={"prompt": "Build a todo app", "use_llm": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "quick"
        assert "result" in data
        
        result = data["result"]
        assert result["original"] == "Build a todo app"
        assert "optimized" in result
        assert "enhancements" in result
        assert isinstance(result["enhancements"], list)
        assert len(result["enhancements"]) > 0
        assert "suggested_tech_stack" in result
        assert "complexity_score" in result
        assert isinstance(result["complexity_score"], int)
        assert 1 <= result["complexity_score"] <= 10
    
    def test_quick_optimize_extracts_entities(self):
        """Test that quick optimization extracts entities"""
        response = requests.post(
            f"{BASE_URL}/api/prompt/optimize",
            json={"prompt": "Build a user management dashboard with tasks", "use_llm": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        result = data["result"]
        
        assert "extracted_entities" in result
        assert isinstance(result["extracted_entities"], list)
        # Should extract User, Task, Dashboard
        entities_lower = [e.lower() for e in result["extracted_entities"]]
        assert any("user" in e for e in entities_lower) or any("task" in e for e in entities_lower)
    
    def test_quick_optimize_extracts_actions(self):
        """Test that quick optimization extracts actions"""
        response = requests.post(
            f"{BASE_URL}/api/prompt/optimize",
            json={"prompt": "Create, update, and delete tasks", "use_llm": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        result = data["result"]
        
        assert "extracted_actions" in result
        assert isinstance(result["extracted_actions"], list)
        # Should extract create, update, delete
        assert "create" in result["extracted_actions"]
    
    def test_quick_optimize_suggests_tech_stack(self):
        """Test that quick optimization suggests appropriate tech stack"""
        response = requests.post(
            f"{BASE_URL}/api/prompt/optimize",
            json={"prompt": "Build a real-time chat application", "use_llm": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        result = data["result"]
        
        assert "suggested_tech_stack" in result
        tech_stack = result["suggested_tech_stack"]
        assert "frontend" in tech_stack
        assert "backend" in tech_stack
        assert "database" in tech_stack
    
    def test_quick_optimize_generates_warnings(self):
        """Test that quick optimization generates appropriate warnings"""
        response = requests.post(
            f"{BASE_URL}/api/prompt/optimize",
            json={"prompt": "app", "use_llm": False}  # Very short prompt
        )
        assert response.status_code == 200
        
        data = response.json()
        result = data["result"]
        
        assert "warnings" in result
        assert isinstance(result["warnings"], list)
        # Should warn about short prompt
        assert any("short" in w.lower() for w in result["warnings"])
    
    def test_get_optimization_patterns(self):
        """Test getting available optimization patterns"""
        response = requests.get(f"{BASE_URL}/api/prompt/patterns")
        assert response.status_code == 200
        
        data = response.json()
        assert "expansion_patterns" in data
        assert "tech_suggestions" in data
        assert "default_stack" in data
        
        assert isinstance(data["expansion_patterns"], list)
        assert len(data["expansion_patterns"]) > 0
        
        default_stack = data["default_stack"]
        assert "frontend" in default_stack
        assert "backend" in default_stack


class TestEnhancedBuild:
    """Test enhanced build engine endpoints"""
    
    project_id = None
    
    def test_enhanced_build_creates_project(self):
        """Test enhanced build creates project with all features"""
        TestEnhancedBuild.project_id = f"test-enhanced-{int(time.time())}"
        
        response = requests.post(
            f"{BASE_URL}/api/build/enhanced",
            json={
                "project_id": TestEnhancedBuild.project_id,
                "project_name": "EnhancedTestApp",
                "specification": {
                    "name": "EnhancedTestApp",
                    "data_model": {
                        "entities": [
                            {"name": "Product", "attributes": [
                                {"name": "name", "type": "string"},
                                {"name": "price", "type": "float"},
                                {"name": "active", "type": "boolean"}
                            ]}
                        ]
                    },
                    "api_contracts": []
                },
                "tech_stack": {
                    "frontend_framework": "nextjs",
                    "backend_framework": "fastapi",
                    "database": "postgresql"
                },
                "include_auth": True,
                "include_tests": True,
                "include_crud": True
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["project_id"] == TestEnhancedBuild.project_id
        assert data["project_name"] == "EnhancedTestApp"
        assert "build_id" in data
        assert "total_artifacts" in data
        assert data["total_artifacts"] > 15  # Should have many files
        
        # Verify features
        assert data["features"]["crud"] == True
        assert data["features"]["auth"] == True
        assert data["features"]["tests"] == True
    
    def test_enhanced_build_creates_crud_routes(self):
        """Test that enhanced build creates CRUD routes"""
        if not TestEnhancedBuild.project_id:
            pytest.skip("No project created")
        
        response = requests.get(
            f"{BASE_URL}/api/build/preview/{TestEnhancedBuild.project_id}"
        )
        assert response.status_code == 200
        
        data = response.json()
        files = data["files"]
        
        # Check for CRUD routes file
        crud_files = [f for f in files if "routes" in f["path"].lower() and "product" in f["path"].lower()]
        assert len(crud_files) > 0, "Should have product CRUD routes"
    
    def test_enhanced_build_creates_auth_module(self):
        """Test that enhanced build creates auth module"""
        if not TestEnhancedBuild.project_id:
            pytest.skip("No project created")
        
        response = requests.get(
            f"{BASE_URL}/api/build/preview/{TestEnhancedBuild.project_id}"
        )
        assert response.status_code == 200
        
        data = response.json()
        files = data["files"]
        
        # Check for auth files
        auth_files = [f for f in files if "auth" in f["path"].lower()]
        assert len(auth_files) >= 3, "Should have auth_models.py, auth_utils.py, auth_routes.py"
    
    def test_enhanced_build_creates_tests(self):
        """Test that enhanced build creates test files"""
        if not TestEnhancedBuild.project_id:
            pytest.skip("No project created")
        
        response = requests.get(
            f"{BASE_URL}/api/build/preview/{TestEnhancedBuild.project_id}"
        )
        assert response.status_code == 200
        
        data = response.json()
        files = data["files"]
        
        # Check for test files
        test_files = [f for f in files if "test_" in f["path"].lower()]
        assert len(test_files) > 0, "Should have test files"
        
        # Check for pytest.ini
        pytest_ini = [f for f in files if "pytest.ini" in f["path"]]
        assert len(pytest_ini) > 0, "Should have pytest.ini"


class TestBuildPreview:
    """Test build preview endpoint"""
    
    project_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a project for preview testing"""
        TestBuildPreview.project_id = f"test-preview-{int(time.time())}"
        
        requests.post(
            f"{BASE_URL}/api/build/enhanced",
            json={
                "project_id": TestBuildPreview.project_id,
                "project_name": "PreviewTestApp",
                "specification": {
                    "name": "PreviewTestApp",
                    "data_model": {
                        "entities": [
                            {"name": "Item", "attributes": [{"name": "name", "type": "string"}]}
                        ]
                    }
                },
                "include_auth": False,
                "include_tests": False,
                "include_crud": True
            }
        )
    
    def test_preview_returns_file_list(self):
        """Test that preview returns list of files"""
        response = requests.get(
            f"{BASE_URL}/api/build/preview/{TestBuildPreview.project_id}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "project_id" in data
        assert "project_name" in data
        assert "total_files" in data
        assert "files" in data
        assert isinstance(data["files"], list)
        assert data["total_files"] > 0
    
    def test_preview_includes_file_details(self):
        """Test that preview includes file details"""
        response = requests.get(
            f"{BASE_URL}/api/build/preview/{TestBuildPreview.project_id}"
        )
        assert response.status_code == 200
        
        data = response.json()
        files = data["files"]
        
        for file in files:
            assert "path" in file
            assert "language" in file
            assert "size" in file
            assert "preview" in file
            assert isinstance(file["size"], int)
    
    def test_preview_404_for_nonexistent(self):
        """Test that preview returns 404 for non-existent project"""
        response = requests.get(
            f"{BASE_URL}/api/build/preview/nonexistent-project-xyz"
        )
        assert response.status_code == 404


class TestZipDownload:
    """Test ZIP download endpoint"""
    
    project_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a project for download testing"""
        TestZipDownload.project_id = f"test-download-{int(time.time())}"
        
        requests.post(
            f"{BASE_URL}/api/build/enhanced",
            json={
                "project_id": TestZipDownload.project_id,
                "project_name": "DownloadTestApp",
                "specification": {
                    "name": "DownloadTestApp",
                    "data_model": {
                        "entities": [
                            {"name": "Item", "attributes": [{"name": "name", "type": "string"}]}
                        ]
                    }
                },
                "include_auth": False,
                "include_tests": False,
                "include_crud": False
            }
        )
    
    def test_download_returns_zip(self):
        """Test that download returns a ZIP file"""
        response = requests.get(
            f"{BASE_URL}/api/build/download/{TestZipDownload.project_id}",
            stream=True
        )
        assert response.status_code == 200
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "application/zip" in content_type or "application/octet-stream" in content_type
        
        # Check that we got some content
        content = response.content
        assert len(content) > 0
        
        # ZIP files start with PK
        assert content[:2] == b'PK', "Response should be a valid ZIP file"
    
    def test_download_404_for_nonexistent(self):
        """Test that download returns 404 for non-existent project"""
        response = requests.get(
            f"{BASE_URL}/api/build/download/nonexistent-project-xyz"
        )
        assert response.status_code == 404


class TestMarketingGeneration:
    """Test marketing content generation endpoints"""
    
    marketing_id = None
    
    def test_generate_marketing_content(self):
        """Test generating marketing content"""
        response = requests.post(
            f"{BASE_URL}/api/marketing/generate",
            json={
                "project_name": "TestProduct",
                "specification": {
                    "name": "TestProduct",
                    "description": "A test product for testing"
                },
                "tech_stack": {
                    "frontend": "react",
                    "backend": "fastapi"
                }
            },
            timeout=90  # LLM calls can be slow
        )
        assert response.status_code == 200
        
        data = response.json()
        TestMarketingGeneration.marketing_id = data.get("id")
        
        assert "id" in data
        assert data["project_name"] == "TestProduct"
        assert "content" in data
        
        content = data["content"]
        assert "tagline" in content
        assert "headline" in content
        assert "description" in content
        assert "features" in content
        assert isinstance(content["features"], list)
        assert "benefits" in content
        assert isinstance(content["benefits"], list)
        assert "cta_primary" in content
    
    def test_marketing_includes_landing_page(self):
        """Test that marketing includes landing page HTML"""
        response = requests.post(
            f"{BASE_URL}/api/marketing/generate",
            json={
                "project_name": "LandingTest",
                "specification": {"name": "LandingTest"},
                "tech_stack": {}
            },
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "landing_page_html" in data
        assert "<!DOCTYPE html>" in data["landing_page_html"]
        assert "LandingTest" in data["landing_page_html"]
    
    def test_marketing_includes_email_templates(self):
        """Test that marketing includes email templates"""
        response = requests.post(
            f"{BASE_URL}/api/marketing/generate",
            json={
                "project_name": "EmailTest",
                "specification": {"name": "EmailTest"},
                "tech_stack": {}
            },
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "email_templates" in data
        emails = data["email_templates"]
        assert "welcome" in emails
        assert "launch_announcement" in emails
    
    def test_marketing_includes_social_posts(self):
        """Test that marketing includes social media posts"""
        response = requests.post(
            f"{BASE_URL}/api/marketing/generate",
            json={
                "project_name": "SocialTest",
                "specification": {"name": "SocialTest"},
                "tech_stack": {}
            },
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "social_posts" in data
        social = data["social_posts"]
        assert "twitter" in social
        assert "linkedin" in social
    
    def test_get_marketing_content(self):
        """Test retrieving previously generated marketing content"""
        if not TestMarketingGeneration.marketing_id:
            pytest.skip("No marketing content generated")
        
        response = requests.get(
            f"{BASE_URL}/api/marketing/content/{TestMarketingGeneration.marketing_id}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == TestMarketingGeneration.marketing_id
        assert "content" in data
    
    def test_get_marketing_404_for_nonexistent(self):
        """Test that get marketing returns 404 for non-existent ID"""
        response = requests.get(
            f"{BASE_URL}/api/marketing/content/nonexistent-id-xyz"
        )
        assert response.status_code == 404


class TestLLMStatus:
    """Test LLM status endpoint"""
    
    def test_llm_status_returns_config(self):
        """Test that LLM status returns configuration"""
        response = requests.get(f"{BASE_URL}/api/llm/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "active"
        assert "configuration" in data
        
        config = data["configuration"]
        assert "mode" in config
        assert config["mode"] in ["cloud", "local", "hybrid"]
        assert "local_available" in config
        assert "cloud_available" in config
    
    def test_llm_status_includes_recommended_models(self):
        """Test that LLM status includes recommended models"""
        response = requests.get(f"{BASE_URL}/api/llm/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommended_models" in data
        assert isinstance(data["recommended_models"], dict)


# Health check test
def test_api_root():
    """Test API root endpoint"""
    response = requests.get(f"{BASE_URL}/api/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["version"] == "2.0.0"
    assert "modules" in data
