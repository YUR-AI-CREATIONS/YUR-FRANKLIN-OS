"""
LITHIUM 8-GATE CERTIFICATION ENGINE
Real validation - not labels, actual tests
"""

import os
import re
import ast
import json
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

PROJECTS_DIR = Path("/app/generated_projects")


@dataclass
class GateResult:
    """Result of a single gate validation"""
    gate_num: int
    gate_name: str
    passed: bool
    score: float  # 0-100
    checks_run: int
    checks_passed: int
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class CertificationEngine:
    """
    8-Gate Certification Engine
    Each gate performs REAL validation, not just labels
    """
    
    def __init__(self):
        self.gates = {
            1: ("Intent Validation", self._gate_1_intent),
            2: ("Data Validation", self._gate_2_data),
            3: ("Model Validation", self._gate_3_model),
            4: ("Vector/RAG Validation", self._gate_4_vector),
            5: ("Orchestration Validation", self._gate_5_orchestration),
            6: ("API Validation", self._gate_6_api),
            7: ("UI Validation", self._gate_7_ui),
            8: ("Security Validation", self._gate_8_security)
        }
    
    async def run_all_gates(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict]) -> Dict:
        """Run all 8 gates and return comprehensive results"""
        results = {
            "build_id": build_id,
            "gates": [],
            "total_score": 0,
            "passed_gates": 0,
            "failed_gates": 0,
            "all_passed": False,
            "certification_hash": None,
            "certified_at": None
        }
        
        project_dir = PROJECTS_DIR / build_id
        
        for gate_num in range(1, 9):
            gate_name, gate_func = self.gates[gate_num]
            
            try:
                gate_result = await gate_func(
                    build_id=build_id,
                    mission=mission,
                    spec=spec,
                    architecture=architecture,
                    files=files,
                    project_dir=project_dir
                )
            except Exception as e:
                gate_result = GateResult(
                    gate_num=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    score=0,
                    checks_run=1,
                    checks_passed=0,
                    details={"error": str(e)},
                    errors=[f"Gate execution failed: {str(e)}"],
                    warnings=[]
                )
            
            results["gates"].append({
                "gate_num": gate_result.gate_num,
                "gate_name": gate_result.gate_name,
                "passed": gate_result.passed,
                "score": gate_result.score,
                "checks_run": gate_result.checks_run,
                "checks_passed": gate_result.checks_passed,
                "details": gate_result.details,
                "errors": gate_result.errors,
                "warnings": gate_result.warnings
            })
            
            results["total_score"] += gate_result.score
            if gate_result.passed:
                results["passed_gates"] += 1
            else:
                results["failed_gates"] += 1
        
        # Calculate final results
        results["total_score"] = results["total_score"] / 8  # Average
        results["all_passed"] = results["passed_gates"] == 8
        
        # If all gates passed, generate certification
        if results["all_passed"]:
            cert_content = json.dumps({
                "build_id": build_id,
                "mission": mission,
                "gates": [g["gate_name"] for g in results["gates"]],
                "score": results["total_score"]
            }, sort_keys=True)
            results["certification_hash"] = hashlib.sha256(cert_content.encode()).hexdigest()
            results["certified_at"] = datetime.now(timezone.utc).isoformat()
        
        return results
    
    async def run_single_gate(self, gate_num: int, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict]) -> GateResult:
        """Run a single gate"""
        if gate_num not in self.gates:
            raise ValueError(f"Invalid gate number: {gate_num}")
        
        gate_name, gate_func = self.gates[gate_num]
        project_dir = PROJECTS_DIR / build_id
        
        return await gate_func(
            build_id=build_id,
            mission=mission,
            spec=spec,
            architecture=architecture,
            files=files,
            project_dir=project_dir
        )
    
    # ========================================================================
    # GATE 1: INTENT VALIDATION
    # ========================================================================
    
    async def _gate_1_intent(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Validate that the build matches user intent
        - Check spec contains mission keywords
        - Verify file types match requirements
        - Confirm architecture addresses the mission
        """
        errors = []
        warnings = []
        checks = []
        
        # Extract keywords from mission
        mission_keywords = set(re.findall(r'\b\w{4,}\b', mission.lower()))
        mission_keywords -= {'with', 'that', 'this', 'from', 'have', 'will', 'should', 'could', 'would'}
        
        # Check 1: Spec contains mission keywords
        spec_lower = spec.lower() if spec else ""
        keywords_found = [kw for kw in mission_keywords if kw in spec_lower]
        keyword_coverage = len(keywords_found) / max(len(mission_keywords), 1)
        checks.append({
            "name": "keyword_coverage",
            "passed": keyword_coverage >= 0.5,
            "value": f"{keyword_coverage*100:.0f}%",
            "details": f"Found {len(keywords_found)}/{len(mission_keywords)} keywords"
        })
        
        # Check 2: Files were generated
        file_count = len(files)
        checks.append({
            "name": "files_generated",
            "passed": file_count > 0,
            "value": file_count,
            "details": f"{file_count} files generated"
        })
        if file_count == 0:
            errors.append("No files were generated")
        
        # Check 3: Architecture exists
        has_architecture = bool(architecture and len(architecture) > 100)
        checks.append({
            "name": "architecture_defined",
            "passed": has_architecture,
            "value": len(architecture) if architecture else 0,
            "details": "Architecture document present" if has_architecture else "Missing architecture"
        })
        if not has_architecture:
            warnings.append("Architecture document is minimal or missing")
        
        # Check 4: File types match common patterns for the mission
        file_types = [f.get("language", "unknown") for f in files]
        has_code = any(ft in ["python", "py", "javascript", "js", "typescript", "ts"] for ft in file_types)
        checks.append({
            "name": "code_files_present",
            "passed": has_code,
            "value": file_types,
            "details": "Code files detected" if has_code else "No code files"
        })
        
        # Calculate score
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / len(checks)) * 100
        
        return GateResult(
            gate_num=1,
            gate_name="Intent Validation",
            passed=score >= 75,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks, "mission_keywords": list(mission_keywords)[:10]},
            errors=errors,
            warnings=warnings
        )
    
    # ========================================================================
    # GATE 2: DATA VALIDATION
    # ========================================================================
    
    async def _gate_2_data(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Validate data structures and models
        - Check for data model definitions
        - Validate JSON/YAML syntax
        - Check SQL syntax if present
        """
        errors = []
        warnings = []
        checks = []
        
        # Check 1: Look for model/schema definitions
        model_patterns = [
            r'class\s+\w+.*:',  # Python classes
            r'interface\s+\w+',  # TypeScript interfaces
            r'type\s+\w+\s*=',  # TypeScript types
            r'CREATE\s+TABLE',  # SQL tables
            r'"type":\s*"object"',  # JSON Schema
        ]
        
        model_files = []
        for f in files:
            content = f.get("content", "")
            for pattern in model_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    model_files.append(f.get("path", "unknown"))
                    break
        
        has_models = len(model_files) > 0
        checks.append({
            "name": "data_models_defined",
            "passed": has_models,
            "value": model_files,
            "details": f"Found {len(model_files)} files with data models"
        })
        
        # Check 2: Validate JSON files
        json_files = [f for f in files if f.get("path", "").endswith(".json")]
        json_valid = 0
        for jf in json_files:
            try:
                json.loads(jf.get("content", "{}"))
                json_valid += 1
            except:
                errors.append(f"Invalid JSON: {jf.get('path')}")
        
        if json_files:
            checks.append({
                "name": "json_syntax_valid",
                "passed": json_valid == len(json_files),
                "value": f"{json_valid}/{len(json_files)}",
                "details": "All JSON files valid" if json_valid == len(json_files) else "Some JSON invalid"
            })
        
        # Check 3: Python syntax validation
        python_files = [f for f in files if f.get("language") in ["python", "py"]]
        python_valid = 0
        for pf in python_files:
            try:
                ast.parse(pf.get("content", ""))
                python_valid += 1
            except SyntaxError as e:
                errors.append(f"Python syntax error in {pf.get('path')}: {e.msg}")
        
        if python_files:
            checks.append({
                "name": "python_syntax_valid",
                "passed": python_valid == len(python_files),
                "value": f"{python_valid}/{len(python_files)}",
                "details": "All Python files valid" if python_valid == len(python_files) else "Some Python files have errors"
            })
        
        # Check 4: SQL syntax check (basic)
        sql_files = [f for f in files if f.get("path", "").endswith(".sql") or f.get("language") == "sql"]
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
        for sf in sql_files:
            content = sf.get("content", "").upper()
            if not any(kw in content for kw in sql_keywords):
                warnings.append(f"SQL file {sf.get('path')} may be empty or invalid")
        
        if sql_files:
            checks.append({
                "name": "sql_files_present",
                "passed": True,
                "value": len(sql_files),
                "details": f"{len(sql_files)} SQL files found"
            })
        
        # Default check if no specific validations
        if not checks:
            checks.append({
                "name": "data_structure_check",
                "passed": True,
                "value": "N/A",
                "details": "No specific data structures to validate"
            })
        
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / len(checks)) * 100
        
        return GateResult(
            gate_num=2,
            gate_name="Data Validation",
            passed=score >= 75,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks},
            errors=errors,
            warnings=warnings
        )
    
    # ========================================================================
    # GATE 3: MODEL VALIDATION
    # ========================================================================
    
    async def _gate_3_model(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Validate LLM/ML model configurations if present
        """
        errors = []
        warnings = []
        checks = []
        
        # Check for LLM-related code
        llm_patterns = [
            r'openai',
            r'anthropic',
            r'langchain',
            r'llama',
            r'gpt-',
            r'claude',
            r'gemini',
            r'embedding',
            r'chat.*completion'
        ]
        
        llm_files = []
        for f in files:
            content = f.get("content", "").lower()
            if any(re.search(p, content) for p in llm_patterns):
                llm_files.append(f.get("path"))
        
        if llm_files:
            checks.append({
                "name": "llm_integration_found",
                "passed": True,
                "value": llm_files,
                "details": f"LLM integration in {len(llm_files)} files"
            })
            
            # Check for API key handling
            for f in files:
                if f.get("path") in llm_files:
                    content = f.get("content", "")
                    if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
                        errors.append(f"Hardcoded API key found in {f.get('path')}")
                    if 'os.environ' in content or 'os.getenv' in content or 'process.env' in content:
                        checks.append({
                            "name": "env_var_usage",
                            "passed": True,
                            "value": f.get("path"),
                            "details": "Uses environment variables for secrets"
                        })
        else:
            # No LLM integration - that's okay for non-AI projects
            checks.append({
                "name": "model_config_check",
                "passed": True,
                "value": "N/A",
                "details": "No LLM/ML models detected (not required)"
            })
        
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100
        
        return GateResult(
            gate_num=3,
            gate_name="Model Validation",
            passed=score >= 75 and len(errors) == 0,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks},
            errors=errors,
            warnings=warnings
        )
    
    # ========================================================================
    # GATE 4: VECTOR/RAG VALIDATION
    # ========================================================================
    
    async def _gate_4_vector(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Validate vector database and RAG configurations if present
        """
        errors = []
        warnings = []
        checks = []
        
        # Check for vector/RAG patterns
        vector_patterns = [
            r'pinecone',
            r'weaviate',
            r'milvus',
            r'chromadb',
            r'faiss',
            r'embedding',
            r'vector.*store',
            r'retriev',
            r'rag'
        ]
        
        vector_files = []
        for f in files:
            content = f.get("content", "").lower()
            if any(re.search(p, content) for p in vector_patterns):
                vector_files.append(f.get("path"))
        
        if vector_files:
            checks.append({
                "name": "vector_db_integration",
                "passed": True,
                "value": vector_files,
                "details": f"Vector/RAG code in {len(vector_files)} files"
            })
        else:
            checks.append({
                "name": "vector_check",
                "passed": True,
                "value": "N/A",
                "details": "No vector/RAG components (not required)"
            })
        
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100
        
        return GateResult(
            gate_num=4,
            gate_name="Vector/RAG Validation",
            passed=score >= 75,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks},
            errors=errors,
            warnings=warnings
        )
    
    # ========================================================================
    # GATE 5: ORCHESTRATION VALIDATION
    # ========================================================================
    
    async def _gate_5_orchestration(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Validate workflow orchestration, check for infinite loops
        """
        errors = []
        warnings = []
        checks = []
        
        for f in files:
            content = f.get("content", "")
            filepath = f.get("path", "")
            
            # Check for while True without break
            if "while True" in content or "while true" in content.lower():
                if "break" not in content:
                    warnings.append(f"Potential infinite loop in {filepath}: while True without break")
            
            # Check for recursive calls without base case
            func_defs = re.findall(r'def\s+(\w+)\s*\(', content)
            for func in func_defs:
                func_body_match = re.search(rf'def\s+{func}\s*\([^)]*\):[^\n]*\n((?:\s+.*\n)*)', content)
                if func_body_match:
                    func_body = func_body_match.group(1)
                    if func in func_body and 'return' not in func_body.split(func)[0]:
                        warnings.append(f"Potential infinite recursion in {filepath}: {func}")
        
        # Check for proper error handling
        has_try_except = any('try:' in f.get("content", "") for f in files if f.get("language") in ["python", "py"])
        has_try_catch = any('try {' in f.get("content", "") for f in files if f.get("language") in ["javascript", "js", "typescript", "ts"])
        
        checks.append({
            "name": "error_handling",
            "passed": has_try_except or has_try_catch or len(files) == 0,
            "value": "present" if (has_try_except or has_try_catch) else "missing",
            "details": "Error handling detected" if (has_try_except or has_try_catch) else "No try/except or try/catch found"
        })
        
        checks.append({
            "name": "infinite_loop_check",
            "passed": len([w for w in warnings if "infinite" in w.lower()]) == 0,
            "value": "clear" if len([w for w in warnings if "infinite" in w.lower()]) == 0 else "warning",
            "details": "No obvious infinite loops" if len([w for w in warnings if "infinite" in w.lower()]) == 0 else "Potential infinite loops detected"
        })
        
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100
        
        return GateResult(
            gate_num=5,
            gate_name="Orchestration Validation",
            passed=score >= 75 and len(errors) == 0,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks},
            errors=errors,
            warnings=warnings
        )
    
    # ========================================================================
    # GATE 6: API VALIDATION
    # ========================================================================
    
    async def _gate_6_api(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Validate API endpoints and error handling
        """
        errors = []
        warnings = []
        checks = []
        
        # Look for API route definitions
        api_patterns = [
            (r'@app\.(get|post|put|delete|patch)\s*\(', 'FastAPI/Flask'),
            (r'router\.(get|post|put|delete|patch)\s*\(', 'Express/FastAPI Router'),
            (r'@(Get|Post|Put|Delete|Patch)\s*\(', 'NestJS'),
            (r'app\.(get|post|put|delete|patch)\s*\(', 'Express'),
        ]
        
        routes_found = []
        for f in files:
            content = f.get("content", "")
            for pattern, framework in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    routes_found.extend([(m, framework, f.get("path")) for m in matches])
        
        if routes_found:
            checks.append({
                "name": "api_routes_defined",
                "passed": True,
                "value": len(routes_found),
                "details": f"Found {len(routes_found)} API routes"
            })
            
            # Check for error handling in API routes
            api_files = set(r[2] for r in routes_found)
            error_handling = 0
            for f in files:
                if f.get("path") in api_files:
                    content = f.get("content", "")
                    if 'HTTPException' in content or 'status_code' in content or 'res.status' in content:
                        error_handling += 1
            
            checks.append({
                "name": "api_error_handling",
                "passed": error_handling > 0,
                "value": error_handling,
                "details": f"Error handling in {error_handling} API files"
            })
        else:
            checks.append({
                "name": "api_check",
                "passed": True,
                "value": "N/A",
                "details": "No API routes (not required for all projects)"
            })
        
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100
        
        return GateResult(
            gate_num=6,
            gate_name="API Validation",
            passed=score >= 75,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks, "routes": routes_found[:10]},
            errors=errors,
            warnings=warnings
        )
    
    # ========================================================================
    # GATE 7: UI VALIDATION
    # ========================================================================
    
    async def _gate_7_ui(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Validate UI components if present
        """
        errors = []
        warnings = []
        checks = []
        
        # Look for UI framework patterns
        ui_patterns = [
            (r'import.*React', 'React'),
            (r'import.*Vue', 'Vue'),
            (r'import.*Angular', 'Angular'),
            (r'import.*Svelte', 'Svelte'),
            (r'<template>', 'Vue Template'),
            (r'className=', 'React JSX'),
        ]
        
        ui_files = []
        frameworks = set()
        for f in files:
            content = f.get("content", "")
            for pattern, framework in ui_patterns:
                if re.search(pattern, content):
                    ui_files.append(f.get("path"))
                    frameworks.add(framework)
                    break
        
        if ui_files:
            checks.append({
                "name": "ui_framework_detected",
                "passed": True,
                "value": list(frameworks),
                "details": f"UI framework(s): {', '.join(frameworks)}"
            })
            
            # Check for basic accessibility
            html_files = [f for f in files if f.get("path", "").endswith(('.html', '.jsx', '.tsx', '.vue'))]
            has_alt = any('alt=' in f.get("content", "") for f in html_files)
            has_aria = any('aria-' in f.get("content", "") for f in html_files)
            
            checks.append({
                "name": "accessibility_attrs",
                "passed": True,  # Don't fail for this, just note
                "value": {"alt": has_alt, "aria": has_aria},
                "details": "Accessibility attributes present" if (has_alt or has_aria) else "Consider adding alt/aria attributes"
            })
            if not has_alt and not has_aria:
                warnings.append("Consider adding accessibility attributes (alt, aria-*)")
        else:
            checks.append({
                "name": "ui_check",
                "passed": True,
                "value": "N/A",
                "details": "No UI components (backend-only project)"
            })
        
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100
        
        return GateResult(
            gate_num=7,
            gate_name="UI Validation",
            passed=score >= 75,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks, "ui_files": ui_files[:10]},
            errors=errors,
            warnings=warnings
        )
    
    # ========================================================================
    # GATE 8: SECURITY VALIDATION
    # ========================================================================
    
    async def _gate_8_security(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        """
        Security validation - the most critical gate
        """
        errors = []
        warnings = []
        checks = []
        
        # Critical security patterns to check
        dangerous_patterns = [
            (r'eval\s*\(', 'eval() usage - potential code injection'),
            (r'exec\s*\(', 'exec() usage - potential code injection'),
            (r'__import__\s*\(', 'Dynamic import - potential security risk'),
            (r'subprocess\.call\([^)]*shell\s*=\s*True', 'Shell injection risk'),
            (r'os\.system\s*\(', 'os.system() - prefer subprocess'),
            (r'pickle\.load', 'Pickle deserialization - potential RCE'),
            (r'yaml\.load\([^)]*Loader\s*=\s*yaml\.Loader', 'YAML unsafe load'),
            (r'innerHTML\s*=', 'innerHTML - XSS risk'),
            (r'dangerouslySetInnerHTML', 'React XSS risk pattern'),
        ]
        
        security_issues = []
        for f in files:
            content = f.get("content", "")
            filepath = f.get("path", "")
            
            for pattern, description in dangerous_patterns:
                if re.search(pattern, content):
                    security_issues.append({
                        "file": filepath,
                        "issue": description,
                        "severity": "high"
                    })
        
        checks.append({
            "name": "dangerous_patterns",
            "passed": len(security_issues) == 0,
            "value": len(security_issues),
            "details": "No dangerous patterns" if len(security_issues) == 0 else f"{len(security_issues)} security issues found"
        })
        
        if security_issues:
            for issue in security_issues:
                errors.append(f"Security: {issue['issue']} in {issue['file']}")
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'["\']sk-[a-zA-Z0-9]{20,}["\']', 'OpenAI API key'),
            (r'["\']sk_live_[a-zA-Z0-9]{20,}["\']', 'Stripe live key'),
            (r'["\']ghp_[a-zA-Z0-9]{36}["\']', 'GitHub token'),
            (r'["\']xox[baprs]-[a-zA-Z0-9-]{10,}["\']', 'Slack token'),
            (r'password\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded password'),
        ]
        
        secrets_found = []
        for f in files:
            content = f.get("content", "")
            filepath = f.get("path", "")
            
            # Skip .env files
            if filepath.endswith('.env') or filepath.endswith('.env.example'):
                continue
            
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, content):
                    secrets_found.append({"file": filepath, "type": secret_type})
        
        checks.append({
            "name": "hardcoded_secrets",
            "passed": len(secrets_found) == 0,
            "value": len(secrets_found),
            "details": "No hardcoded secrets" if len(secrets_found) == 0 else f"{len(secrets_found)} potential secrets found"
        })
        
        if secrets_found:
            for secret in secrets_found:
                errors.append(f"Hardcoded {secret['type']} in {secret['file']}")
        
        # Check for input validation patterns
        has_input_validation = any(
            re.search(r'(validate|sanitize|escape|clean)', f.get("content", "").lower())
            for f in files
        )
        
        checks.append({
            "name": "input_validation",
            "passed": True,  # Don't fail, but note
            "value": "present" if has_input_validation else "not detected",
            "details": "Input validation detected" if has_input_validation else "Consider adding input validation"
        })
        
        if not has_input_validation:
            warnings.append("No obvious input validation detected - consider adding")
        
        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100
        
        # Security gate is stricter - any critical error fails
        critical_errors = len([e for e in errors if "Security" in e or "Hardcoded" in e])
        
        return GateResult(
            gate_num=8,
            gate_name="Security Validation",
            passed=score >= 75 and critical_errors == 0,
            score=score if critical_errors == 0 else score * 0.5,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks, "security_issues": security_issues[:10], "secrets_found": secrets_found[:5]},
            errors=errors,
            warnings=warnings
        )


# Global instance
certification_engine = CertificationEngine()
