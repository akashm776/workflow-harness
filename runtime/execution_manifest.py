from __future__ import annotations

from typing import Any, Mapping


def _artifact_lifecycle_state_for_execution_status(execution_status: str) -> str:
    if execution_status == "ready_to_execute":
        return "ready_to_run"
    if execution_status == "blocked":
        return "failed"
    raise ValueError(f"unsupported execution_status: {execution_status}")


def build_execution_manifest(
    *,
    node_id: str,
    workflow_revision_id: str,
    verifier_result: Mapping[str, Any] | None,
    execution_status: str,
) -> dict[str, Any]:
    return {
        "schema_version": "m1",
        "node_id": node_id,
        "workflow_revision_id": workflow_revision_id,
        "artifact_lifecycle_state": _artifact_lifecycle_state_for_execution_status(
            execution_status
        ),
        "execution_status": execution_status,
        "verifier_result": (
            dict(verifier_result) if verifier_result is not None else None
        ),
        "started_at": None,
        "completed_at": None,
        "produced_evidence": [],
        "side_effects": [],
    }
