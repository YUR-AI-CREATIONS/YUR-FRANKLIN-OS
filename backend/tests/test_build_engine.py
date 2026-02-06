"""
Build Engine Phase 2 Tests
Tests for code generation and file writing functionality.
- POST /api/build/generate - Creates code artifacts
- POST /api/build/write - Writes actual files to disk
- GET /api/build/tree - Returns file tree structure
- Validates generated files exist on disk with valid syntax
"""

import pytest
import requests
import os
import json
import subprocess
from pathlib import Path

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test project configuration
TEST_PROJECT_ID = "test-build-engine-project"
TEST_PROJECT_NAME = "TestBuildProject"
TEST_OUTPUT_DIR = "/app/generated"


class TestBuildEngineGenerate:
    """Tests for POST /api/build/generate endpoint"""
    
    def test_generate_build_creates_artifacts(self):
        """Test that generate endpoint creates code artifacts"""
        payload = {
            "project_id": TEST_PROJECT_ID,
            "project_name": TEST_PROJECT_NAME,
            "specification": {
                "name": "Test Build Project",
                "components": [],
                "data_model": {
                    "entities": [
                        {
                            "name": "Product",
                            "attributes": [
                                {"name": "name", "type": "string"},
                                {"name": "price", "type": "float"},
                                {"name": "in_stock", "type": "boolean"}
                            ]
                        },
                        {
                            "name": "Order",
                            "attributes": [
                                {"name": "order_number", "type": "string"},
                                {"name": "total", "type": "float"},
                                {"name": "created_at", "type": "datetime"}
                            ]
                        }
                    ]
                },
                "api_contracts": [
                    {"endpoint": "/products", "method": "GET"},
                    {"endpoint": "/products", "method": "POST"},
                    {"endpoint": "/orders", "method": "GET"}
                ],
                "security": {}
            },
            "tech_stack": {
                "frontend_framework": "nextjs",
                "backend_framework": "fastapi",
                "database": "postgresql",
                "css_framework": "tailwindcss",
                "ci_cd": "github_actions"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/build/generate", json=payload)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "build_id" in data, "Response should contain build_id"
        assert "project_name" in data, "Response should contain project_name"
        assert data["project_name"] == TEST_PROJECT_NAME
        assert "total_artifacts" in data, "Response should contain total_artifacts"
        assert data["total_artifacts"] >= 14, f"Expected at least 14 artifacts, got {data['total_artifacts']}"
        assert "artifacts_by_language" in data, "Response should contain artifacts_by_language"
        
        # Verify artifacts by language
        artifacts = data["artifacts_by_language"]
        assert "python" in artifacts, "Should have Python artifacts"
        assert "typescript" in artifacts, "Should have TypeScript artifacts"
        assert "json" in artifacts, "Should have JSON artifacts"
        assert "yaml" in artifacts, "Should have YAML artifacts"
        assert "sql" in artifacts, "Should have SQL artifacts"
        assert "dockerfile" in artifacts, "Should have Dockerfile artifacts"
        
        # Verify tech stack in response
        assert "tech_stack" in data
        assert data["tech_stack"]["frontend_framework"] == "nextjs"
        assert data["tech_stack"]["backend_framework"] == "fastapi"
        assert data["tech_stack"]["database"] == "postgresql"
    
    def test_generate_build_with_react_stack(self):
        """Test generation with React instead of Next.js"""
        payload = {
            "project_id": "test-react-project",
            "project_name": "ReactTestProject",
            "specification": {
                "name": "React Test",
                "data_model": {"entities": []},
                "api_contracts": [],
                "security": {}
            },
            "tech_stack": {
                "frontend_framework": "react",
                "backend_framework": "fastapi",
                "database": "mongodb"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/build/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["tech_stack"]["frontend_framework"] == "react"
        assert data["tech_stack"]["database"] == "mongodb"


class TestBuildEngineWrite:
    """Tests for POST /api/build/write endpoint"""
    
    def test_write_to_disk_creates_files(self):
        """Test that write endpoint creates actual files on disk"""
        # First generate the build
        generate_payload = {
            "project_id": "test-write-project",
            "project_name": "WriteTestProject",
            "specification": {
                "name": "Write Test Project",
                "data_model": {
                    "entities": [
                        {
                            "name": "Item",
                            "attributes": [
                                {"name": "name", "type": "string"},
                                {"name": "quantity", "type": "integer"}
                            ]
                        }
                    ]
                },
                "api_contracts": [
                    {"endpoint": "/items", "method": "GET"}
                ],
                "security": {}
            },
            "tech_stack": {
                "frontend_framework": "nextjs",
                "backend_framework": "fastapi",
                "database": "postgresql",
                "css_framework": "tailwindcss",
                "ci_cd": "github_actions"
            }
        }
        
        gen_response = requests.post(f"{BASE_URL}/api/build/generate", json=generate_payload)
        assert gen_response.status_code == 200, f"Generate failed: {gen_response.text}"
        
        # Now write to disk
        write_payload = {
            "project_id": "test-write-project",
            "output_directory": TEST_OUTPUT_DIR
        }
        
        response = requests.post(f"{BASE_URL}/api/build/write", json=write_payload)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert data["success"] == True, "Write should succeed"
        assert "output_directory" in data
        assert "WriteTestProject" in data["output_directory"]
        assert "total_files_written" in data
        assert data["total_files_written"] >= 14, f"Expected at least 14 files, got {data['total_files_written']}"
        assert "files" in data
        assert len(data["files"]) >= 14
        
        # Verify file structure in response
        file_paths = [f["relative_path"] for f in data["files"]]
        assert any("main.py" in p for p in file_paths), "Should have main.py"
        assert any("package.json" in p for p in file_paths), "Should have package.json"
        assert any("schema.sql" in p for p in file_paths), "Should have schema.sql"
        assert any("docker-compose.yml" in p for p in file_paths), "Should have docker-compose.yml"
        assert any("Dockerfile" in p for p in file_paths), "Should have Dockerfile"
    
    def test_write_without_generate_fails(self):
        """Test that write fails if generate wasn't called first"""
        write_payload = {
            "project_id": "non-existent-project",
            "output_directory": TEST_OUTPUT_DIR
        }
        
        response = requests.post(f"{BASE_URL}/api/build/write", json=write_payload)
        
        # Should return 404 since build doesn't exist
        assert response.status_code == 404


class TestBuildEngineTree:
    """Tests for GET /api/build/tree endpoint"""
    
    def test_get_file_tree_structure(self):
        """Test that tree endpoint returns proper file structure"""
        # First generate a build
        generate_payload = {
            "project_id": "test-tree-project",
            "project_name": "TreeTestProject",
            "specification": {
                "name": "Tree Test",
                "data_model": {"entities": []},
                "api_contracts": [],
                "security": {}
            },
            "tech_stack": {
                "frontend_framework": "nextjs",
                "backend_framework": "fastapi",
                "database": "postgresql"
            }
        }
        
        gen_response = requests.post(f"{BASE_URL}/api/build/generate", json=generate_payload)
        assert gen_response.status_code == 200
        
        # Get tree
        response = requests.get(f"{BASE_URL}/api/build/tree/test-tree-project")
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "project_id" in data
        assert data["project_id"] == "test-tree-project"
        assert "project_name" in data
        assert data["project_name"] == "TreeTestProject"
        assert "tree" in data
        
        # Verify tree structure
        tree = data["tree"]
        assert "TreeTestProject" in tree, "Tree should have project root"
        project_tree = tree["TreeTestProject"]
        assert "frontend" in project_tree or "children" in project_tree
        assert "backend" in project_tree or "children" in project_tree
    
    def test_tree_for_nonexistent_project(self):
        """Test tree endpoint returns 404 for non-existent project"""
        response = requests.get(f"{BASE_URL}/api/build/tree/nonexistent-project-xyz")
        assert response.status_code == 404


class TestGeneratedFilesOnDisk:
    """Tests to verify actual files exist on disk with valid syntax"""
    
    def test_taskmanager_files_exist(self):
        """Verify TaskManager project files exist on disk"""
        base_path = Path("/app/generated/TaskManager")
        
        # Check directory exists
        assert base_path.exists(), f"TaskManager directory should exist at {base_path}"
        
        # Check key files exist
        expected_files = [
            "backend/app/main.py",
            "backend/app/models.py",
            "backend/app/routes.py",
            "backend/requirements.txt",
            "backend/Dockerfile",
            "frontend/package.json",
            "frontend/app/layout.tsx",
            "frontend/app/page.tsx",
            "frontend/tailwind.config.ts",
            "frontend/Dockerfile",
            "database/schema.sql",
            "docker-compose.yml",
            ".github/workflows/ci.yml",
            ".github/workflows/deploy.yml",
            "sgp-manifest.json"
        ]
        
        for file_path in expected_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"File should exist: {full_path}"
    
    def test_python_files_valid_syntax(self):
        """Verify generated Python files have valid syntax"""
        python_files = [
            "/app/generated/TaskManager/backend/app/main.py",
            "/app/generated/TaskManager/backend/app/models.py",
            "/app/generated/TaskManager/backend/app/routes.py"
        ]
        
        for py_file in python_files:
            if Path(py_file).exists():
                result = subprocess.run(
                    ["python3", "-m", "py_compile", py_file],
                    capture_output=True,
                    text=True
                )
                assert result.returncode == 0, f"Python syntax error in {py_file}: {result.stderr}"
    
    def test_yaml_files_valid_syntax(self):
        """Verify generated YAML files have valid syntax"""
        import yaml
        
        yaml_files = [
            "/app/generated/TaskManager/docker-compose.yml",
            "/app/generated/TaskManager/.github/workflows/ci.yml",
            "/app/generated/TaskManager/.github/workflows/deploy.yml"
        ]
        
        for yaml_file in yaml_files:
            if Path(yaml_file).exists():
                with open(yaml_file, 'r') as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"YAML syntax error in {yaml_file}: {e}")
    
    def test_json_files_valid_syntax(self):
        """Verify generated JSON files have valid syntax"""
        json_files = [
            "/app/generated/TaskManager/frontend/package.json",
            "/app/generated/TaskManager/sgp-manifest.json"
        ]
        
        for json_file in json_files:
            if Path(json_file).exists():
                with open(json_file, 'r') as f:
                    try:
                        json.load(f)
                    except json.JSONDecodeError as e:
                        pytest.fail(f"JSON syntax error in {json_file}: {e}")
    
    def test_manifest_has_correct_file_count(self):
        """Verify manifest reports correct number of files"""
        manifest_path = Path("/app/generated/TaskManager/sgp-manifest.json")
        
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            assert "total_files" in manifest
            assert manifest["total_files"] >= 14, f"Expected at least 14 files, got {manifest['total_files']}"
            assert "files" in manifest
            assert len(manifest["files"]) >= 14


class TestFullBuildWorkflow:
    """End-to-end test of the complete build workflow"""
    
    def test_full_workflow_generate_write_verify(self):
        """Test complete flow: generate → write → verify files on disk"""
        project_name = "E2ETestProject"
        project_id = "e2e-test-project"
        
        # Step 1: Generate build
        generate_payload = {
            "project_id": project_id,
            "project_name": project_name,
            "specification": {
                "name": "E2E Test Project",
                "data_model": {
                    "entities": [
                        {
                            "name": "Customer",
                            "attributes": [
                                {"name": "email", "type": "string"},
                                {"name": "name", "type": "string"},
                                {"name": "active", "type": "boolean"}
                            ]
                        }
                    ]
                },
                "api_contracts": [
                    {"endpoint": "/customers", "method": "GET"},
                    {"endpoint": "/customers", "method": "POST"}
                ],
                "security": {}
            },
            "tech_stack": {
                "frontend_framework": "nextjs",
                "backend_framework": "fastapi",
                "database": "postgresql",
                "css_framework": "tailwindcss",
                "ci_cd": "github_actions"
            }
        }
        
        gen_response = requests.post(f"{BASE_URL}/api/build/generate", json=generate_payload)
        assert gen_response.status_code == 200, f"Generate failed: {gen_response.text}"
        gen_data = gen_response.json()
        assert gen_data["total_artifacts"] >= 14
        
        # Step 2: Write to disk
        write_payload = {
            "project_id": project_id,
            "output_directory": TEST_OUTPUT_DIR
        }
        
        write_response = requests.post(f"{BASE_URL}/api/build/write", json=write_payload)
        assert write_response.status_code == 200, f"Write failed: {write_response.text}"
        write_data = write_response.json()
        assert write_data["success"] == True
        assert write_data["total_files_written"] >= 14
        
        # Step 3: Verify files exist on disk
        project_path = Path(f"{TEST_OUTPUT_DIR}/{project_name}")
        assert project_path.exists(), f"Project directory should exist: {project_path}"
        
        # Verify key files
        assert (project_path / "backend/app/main.py").exists()
        assert (project_path / "frontend/package.json").exists()
        assert (project_path / "docker-compose.yml").exists()
        assert (project_path / "sgp-manifest.json").exists()
        
        # Step 4: Verify Python syntax
        main_py = project_path / "backend/app/main.py"
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(main_py)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Generated main.py has syntax error: {result.stderr}"
        
        # Step 5: Get tree and verify structure
        tree_response = requests.get(f"{BASE_URL}/api/build/tree/{project_id}")
        assert tree_response.status_code == 200
        tree_data = tree_response.json()
        assert tree_data["project_name"] == project_name


class TestBuildEngineArtifacts:
    """Tests for artifact retrieval endpoints"""
    
    def test_get_artifacts_list(self):
        """Test getting list of artifacts for a project"""
        # First generate
        generate_payload = {
            "project_id": "test-artifacts-project",
            "project_name": "ArtifactsTestProject",
            "specification": {
                "name": "Artifacts Test",
                "data_model": {"entities": []},
                "api_contracts": [],
                "security": {}
            },
            "tech_stack": {
                "frontend_framework": "nextjs",
                "backend_framework": "fastapi",
                "database": "postgresql"
            }
        }
        
        gen_response = requests.post(f"{BASE_URL}/api/build/generate", json=generate_payload)
        assert gen_response.status_code == 200
        
        # Get artifacts
        response = requests.get(f"{BASE_URL}/api/build/artifacts/test-artifacts-project")
        
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert "artifacts" in data
        assert len(data["artifacts"]) >= 10
        
        # Verify artifact structure
        for artifact in data["artifacts"]:
            assert "id" in artifact
            assert "path" in artifact
            assert "language" in artifact
            assert "type" in artifact
    
    def test_get_deployment_config(self):
        """Test getting deployment configuration"""
        # First generate with serverless config
        generate_payload = {
            "project_id": "test-deploy-project",
            "project_name": "DeployTestProject",
            "specification": {
                "name": "Deploy Test",
                "data_model": {"entities": []},
                "api_contracts": [],
                "security": {}
            },
            "tech_stack": {
                "frontend_framework": "nextjs",
                "backend_framework": "fastapi",
                "database": "postgresql",
                "serverless": "vercel"
            }
        }
        
        gen_response = requests.post(f"{BASE_URL}/api/build/generate", json=generate_payload)
        assert gen_response.status_code == 200
        
        # Get deployment config
        response = requests.get(f"{BASE_URL}/api/build/deployment/test-deploy-project")
        
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert "deployment_config" in data
        assert "environment_variables" in data
        
        # Verify environment variables
        env_vars = data["environment_variables"]
        assert "DATABASE_URL" in env_vars
        assert "NODE_ENV" in env_vars


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_projects():
    """Cleanup test-generated projects after tests complete"""
    yield
    # Cleanup generated test projects
    import shutil
    test_projects = [
        "/app/generated/WriteTestProject",
        "/app/generated/TreeTestProject",
        "/app/generated/E2ETestProject",
        "/app/generated/ArtifactsTestProject",
        "/app/generated/DeployTestProject",
        "/app/generated/ReactTestProject"
    ]
    for project in test_projects:
        if Path(project).exists():
            try:
                shutil.rmtree(project)
            except Exception:
                pass
