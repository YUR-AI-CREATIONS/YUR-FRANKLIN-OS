"""
ConfigHydrator: derive a deterministic node graph from backend code.

For now, we parse Python source/AST to produce a linear 12-station
representation (the Helix topology). This stub can later ingest bytecode
or richer metadata.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Dict, Any

HELIX_STATIONS = [
    "Source_Ingestion",
    "Syntax_Decomposition",
    "Static_Analysis",
    "Feature_Extraction",
    "Confidence_Filtering",
    "Data_Normalization",
    "Heuristic_Inference",
    "Spatial_Validation",
    "Readiness_Scoring",
    "Artifact_Generation",
    "Performance_Telemetry",
    "Evolutionary_Commit",
]


def hydrate_from_source(path: Path) -> Dict[str, Any]:
    """
    Parse Python source to derive a deterministic node list.
    This does not execute code; it only inspects AST to flag presence
    of functions/classes that might inform station annotations.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    symbols = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]

    nodes = []
    edges = []
    for idx, name in enumerate(HELIX_STATIONS):
        nodes.append(
            {
                "id": f"station_{idx+1}",
                "name": name,
                "label": name.replace("_", " "),
                "order": idx,
                "annotations": {
                    "symbols_present": symbols,
                    "confidence": 1.0 if symbols else 0.5,
                },
            }
        )
        if idx < len(HELIX_STATIONS) - 1:
            edges.append(
                {
                    "id": f"edge_{idx+1}_{idx+2}",
                    "source": f"station_{idx+1}",
                    "target": f"station_{idx+2}",
                    "type": "linear",
                }
            )

    return {
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "source_file": str(path),
            "station_count": len(nodes),
            "topology": "helix_linear",
        },
    }


def hydrate_from_bytes(payload: bytes) -> Dict[str, Any]:
    """
    Placeholder for bytecode parsing; currently routes to no-op topology.
    """
    return {
        "nodes": [
            {"id": f"station_{idx+1}", "name": name, "label": name.replace("_", " "), "order": idx}
            for idx, name in enumerate(HELIX_STATIONS)
        ],
        "edges": [
            {"id": f"edge_{i+1}_{i+2}", "source": f"station_{i+1}", "target": f"station_{i+2}", "type": "linear"}
            for i in range(len(HELIX_STATIONS) - 1)
        ],
        "meta": {"source_file": "bytecode", "station_count": len(HELIX_STATIONS), "topology": "helix_linear"},
    }
