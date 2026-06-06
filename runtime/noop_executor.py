from __future__ import annotations

from typing import Any, Mapping


def execute_noop_node(execution_manifest: Mapping[str, Any]) -> dict[str, Any]:
    if execution_manifest.get("execution_status") != "ready_to_execute":
        return {
            "ok": False,
            "execution_status": "blocked",
            "produced_evidence": [],
            "side_effects": [],
        }

    return {
        "ok": True,
        "execution_status": "completed",
        "produced_evidence": [],
        "side_effects": [],
    }
