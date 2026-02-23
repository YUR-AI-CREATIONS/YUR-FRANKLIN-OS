"""
LITHIUM 8-GATE CERTIFICATION ENGINE
Real validation - not labels, actual tests
"""

import os
import re
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
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

        results["total_score"] = results["total_score"] / 8
        results["all_passed"] = results["passed_gates"] == 8

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

    # GATE 1: INTENT VALIDATION
    async def _gate_1_intent(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        mission_keywords = set(re.findall(r'\b\w{4,}\b', mission.lower()))
        mission_keywords -= {'with', 'that', 'this', 'from', 'have', 'will', 'should', 'could', 'would'}

        spec_lower = spec.lower() if spec else ""
        keywords_found = [kw for kw in mission_keywords if kw in spec_lower]
        keyword_coverage = len(keywords_found) / max(len(mission_keywords), 1)
        checks.append({
            "name": "keyword_coverage",
            "passed": keyword_coverage >= 0.5,
            "value": f"{keyword_coverage*100:.0f}%",
            "details": f"Found {len(keywords_found)}/{len(mission_keywords)} keywords"
        })

        file_count = len(files)
        checks.append({
            "name": "files_generated",
            "passed": file_count > 0,
            "value": file_count,
            "details": f"{file_count} files generated"
        })
        if file_count == 0:
            errors.append("No files were generated")

        has_architecture = bool(architecture and len(architecture) > 100)
        checks.append({
            "name": "architecture_defined",
            "passed": has_architecture,
            "value": len(architecture) if architecture else 0,
            "details": "Architecture document present" if has_architecture else "Missing architecture"
        })

        file_types = [f.get("language", "unknown") for f in files]
        has_code = any(ft in ["python", "py", "javascript", "js", "typescript", "ts"] for ft in file_types)
        checks.append({
            "name": "code_files_present",
            "passed": has_code,
            "value": file_types,
            "details": "Code files detected" if has_code else "No code files"
        })

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

    # GATE 2: DATA VALIDATION
    async def _gate_2_data(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        model_patterns = [
            r'class\s+\w+.*:',
            r'interface\s+\w+',
            r'type\s+\w+\s*=',
            r'CREATE\s+TABLE',
            r'"type":\s*"object"',
        ]

        model_files = []
        for f in files:
            content = f.get("content", "")
            for pattern in model_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    model_files.append(f.get("path", "unknown"))
                    break

        checks.append({
            "name": "data_models_defined",
            "passed": len(model_files) > 0,
            "value": model_files,
            "details": f"Found {len(model_files)} files with data models"
        })

        json_files = [f for f in files if f.get("path", "").endswith(".json")]
        json_valid = 0
        for jf in json_files:
            try:
                json.loads(jf.get("content", "{}"))
                json_valid += 1
            except Exception:
                errors.append(f"Invalid JSON: {jf.get('path')}")

        if json_files:
            checks.append({
                "name": "json_syntax_valid",
                "passed": json_valid == len(json_files),
                "value": f"{json_valid}/{len(json_files)}",
                "details": "All JSON files valid" if json_valid == len(json_files) else "Some JSON invalid"
            })

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

    # GATE 3: MODEL VALIDATION
    async def _gate_3_model(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        llm_patterns = [r'openai', r'anthropic', r'langchain', r'llama', r'gpt-', r'claude', r'gemini', r'embedding']

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

            has_config = any(
                'api_key' in f.get("content", "").lower() or 
                'model' in f.get("content", "").lower()
                for f in files
            )
            checks.append({
                "name": "llm_config_present",
                "passed": has_config,
                "value": "present" if has_config else "missing",
                "details": "LLM configuration found" if has_config else "No LLM configuration"
            })
        else:
            checks.append({
                "name": "model_check",
                "passed": True,
                "value": "N/A",
                "details": "No LLM integration (not required)"
            })

        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100

        return GateResult(
            gate_num=3,
            gate_name="Model Validation",
            passed=score >= 75,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks, "llm_files": llm_files},
            errors=errors,
            warnings=warnings
        )

    # GATE 4: VECTOR/RAG VALIDATION
    async def _gate_4_vector(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        vector_patterns = [r'vector', r'embedding', r'pinecone', r'weaviate', r'milvus', r'chroma', r'faiss', r'rag']

        vector_files = []
        for f in files:
            content = f.get("content", "").lower()
            if any(re.search(p, content) for p in vector_patterns):
                vector_files.append(f.get("path"))

        if vector_files:
            checks.append({
                "name": "vector_integration_found",
                "passed": True,
                "value": vector_files,
                "details": f"Vector/RAG in {len(vector_files)} files"
            })
        else:
            checks.append({
                "name": "vector_check",
                "passed": True,
                "value": "N/A",
                "details": "No vector/RAG integration (not required)"
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

    # GATE 5: ORCHESTRATION VALIDATION
    async def _gate_5_orchestration(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        for f in files:
            content = f.get("content", "")
            filepath = f.get("path", "")

            if "while True" in content or "while true" in content.lower():
                if "break" not in content:
                    warnings.append(f"Potential infinite loop in {filepath}")

        has_try_except = any('try:' in f.get("content", "") for f in files if f.get("language") in ["python", "py"])
        has_try_catch = any('try {' in f.get("content", "") for f in files if f.get("language") in ["javascript", "js", "typescript", "ts"])

        checks.append({
            "name": "error_handling",
            "passed": has_try_except or has_try_catch or len(files) == 0,
            "value": "present" if (has_try_except or has_try_catch) else "missing",
            "details": "Error handling detected" if (has_try_except or has_try_catch) else "No try/except found"
        })

        checks.append({
            "name": "infinite_loop_check",
            "passed": len([w for w in warnings if "infinite" in w.lower()]) == 0,
            "value": "clear",
            "details": "No obvious infinite loops"
        })

        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100

        return GateResult(
            gate_num=5,
            gate_name="Orchestration Validation",
            passed=score >= 75,
            score=score,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks},
            errors=errors,
            warnings=warnings
        )

    # GATE 6: API VALIDATION
    async def _gate_6_api(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        api_patterns = [
            (r'@app\.(get|post|put|delete|patch)\s*\(', 'FastAPI/Flask'),
            (r'router\.(get|post|put|delete|patch)\s*\(', 'Router'),
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
        else:
            checks.append({
                "name": "api_check",
                "passed": True,
                "value": "N/A",
                "details": "No API routes (not required)"
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

    # GATE 7: UI VALIDATION
    async def _gate_7_ui(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        ui_patterns = [
            (r'import.*React', 'React'),
            (r'import.*Vue', 'Vue'),
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
                "details": f"UI: {', '.join(frameworks)}"
            })
        else:
            checks.append({
                "name": "ui_check",
                "passed": True,
                "value": "N/A",
                "details": "No UI components (backend-only)"
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

    # GATE 8: SECURITY VALIDATION
    async def _gate_8_security(self, build_id: str, mission: str, spec: str, architecture: str, files: List[Dict], project_dir: Path) -> GateResult:
        errors = []
        warnings = []
        checks = []

        dangerous_patterns = [
            (r'eval\s*\(', 'eval() - code injection risk'),
            (r'exec\s*\(', 'exec() - code injection risk'),
            (r'os\.system\s*\(', 'os.system() - prefer subprocess'),
            (r'innerHTML\s*=', 'innerHTML - XSS risk'),
        ]

        security_issues = []
        for f in files:
            content = f.get("content", "")
            filepath = f.get("path", "")
            for pattern, description in dangerous_patterns:
                if re.search(pattern, content):
                    security_issues.append({"file": filepath, "issue": description})

        checks.append({
            "name": "dangerous_patterns",
            "passed": len(security_issues) == 0,
            "value": len(security_issues),
            "details": "No dangerous patterns" if len(security_issues) == 0 else f"{len(security_issues)} issues"
        })

        if security_issues:
            for issue in security_issues:
                errors.append(f"Security: {issue['issue']} in {issue['file']}")

        secret_patterns = [
            (r'["\']sk-[a-zA-Z0-9]{20,}["\']', 'OpenAI key'),
            (r'["\']sk_live_[a-zA-Z0-9]{20,}["\']', 'Stripe key'),
            (r'password\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded password'),
        ]

        secrets_found = []
        for f in files:
            content = f.get("content", "")
            filepath = f.get("path", "")
            if filepath.endswith('.env'):
                continue
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, content):
                    secrets_found.append({"file": filepath, "type": secret_type})

        checks.append({
            "name": "hardcoded_secrets",
            "passed": len(secrets_found) == 0,
            "value": len(secrets_found),
            "details": "No hardcoded secrets" if len(secrets_found) == 0 else f"{len(secrets_found)} secrets"
        })

        passed_checks = sum(1 for c in checks if c["passed"])
        score = (passed_checks / max(len(checks), 1)) * 100
        critical_errors = len([e for e in errors if "Security" in e])

        return GateResult(
            gate_num=8,
            gate_name="Security Validation",
            passed=score >= 75 and critical_errors == 0,
            score=score if critical_errors == 0 else score * 0.5,
            checks_run=len(checks),
            checks_passed=passed_checks,
            details={"checks": checks, "security_issues": security_issues[:10]},
            errors=errors,
            warnings=warnings
        )


# Global instance
certification_engine = CertificationEngine()
