"""
Minimal AST-based safety checks before accepting generated code.
"""
import ast
from typing import Dict, Any, Tuple, List

BANNED_CALLS = {("os", "system"), ("subprocess", "call"), ("subprocess", "Popen")}


def _is_banned(node: ast.AST) -> bool:
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            mod = node.func.value.id
            name = node.func.attr
            if (mod, name) in BANNED_CALLS:
                return True
        if isinstance(node.func, ast.Name):
            if node.func.id in {"exec", "eval"}:
                return True
    return False


def check_code_safety(file_contents: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Inspect generated code content for banned calls and syntax validity.
    Returns (ok, issues).
    """
    issues: List[str] = []
    for path, content in (file_contents or {}).items():
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            issues.append(f"{path}: syntax error {e}")
            continue
        for node in ast.walk(tree):
            if _is_banned(node):
                issues.append(f"{path}: banned call detected")
    return (len(issues) == 0, issues)
