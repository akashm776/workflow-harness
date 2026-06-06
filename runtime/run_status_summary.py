"""Read-only, fail-soft operator summary for a safe no-op run directory.

This is an **opt-in** richer view layered on top of the existence-only
``inspect_run_directory``. Unlike that function, this one parses a few known local
run artifacts read-only to surface compile/execution status. It:

- never writes anything,
- never raises on missing/unreadable/malformed JSON (such fields become ``None``
  or ``"unknown"``),
- reads only known local run artifacts, never tools/connectors/network,
- does not change the existence-only inspection path or its contract.

The existence-only `inspect_run_directory` remains the default boundary; this
summary is a separate, additive surface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.run_status import inspect_run_directory


def _safe_load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _get_str(value: Any, key: str) -> str | None:
    if isinstance(value, dict):
        field = value.get(key)
        if isinstance(field, str):
            return field
    return None


def _extract_candidate_workflow(run_path: Path) -> dict[str, Any] | None:
    """Fail-soft, display-only view of the candidate WorkflowSpec proposal.

    Reads ``<run-dir>/candidate/WorkflowSpec.json`` read-only. Returns ``None``
    when the file is missing/unreadable/malformed or not an object. Keeps only
    string-typed fields, skips malformed node/edge entries, and preserves order.
    This inspects a non-authoritative proposal artifact for display only.
    """

    workflow_spec = _safe_load_json(run_path / "candidate" / "WorkflowSpec.json")
    if not isinstance(workflow_spec, dict):
        return None

    nodes: list[dict[str, Any]] = []
    raw_nodes = workflow_spec.get("nodes")
    if isinstance(raw_nodes, list):
        for raw_node in raw_nodes:
            node_id = _get_str(raw_node, "node_id")
            node_type = _get_str(raw_node, "node_type")
            if node_id is None or node_type is None:
                continue
            node: dict[str, Any] = {"node_id": node_id, "node_type": node_type}
            display_name = _get_str(raw_node, "display_name")
            if display_name is not None:
                node["display_name"] = display_name
            nodes.append(node)

    edges: list[dict[str, Any]] = []
    raw_edges = workflow_spec.get("edges")
    if isinstance(raw_edges, list):
        for raw_edge in raw_edges:
            from_node_id = _get_str(raw_edge, "from_node_id")
            to_node_id = _get_str(raw_edge, "to_node_id")
            if from_node_id is None or to_node_id is None:
                continue
            edge: dict[str, Any] = {
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
            }
            edge_type = _get_str(raw_edge, "edge_type")
            if edge_type is not None:
                edge["edge_type"] = edge_type
            edges.append(edge)

    return {
        "workflow_id": _get_str(workflow_spec, "workflow_id"),
        "workflow_revision_id": _get_str(workflow_spec, "workflow_revision_id"),
        "nodes": nodes,
        "edges": edges,
    }


def summarize_run_directory(run_dir: str | Path) -> dict[str, Any]:
    run_path = Path(run_dir)
    inspection = inspect_run_directory(run_path)

    compilation_report = _safe_load_json(run_path / "CompilationReport.json")
    execution_manifest = _safe_load_json(run_path / "ExecutionManifest.json")
    execution_result = _safe_load_json(run_path / "ExecutionResult.json")
    effective_policy = _safe_load_json(run_path / "EffectivePolicy.json")

    compilation_status = _get_str(compilation_report, "status") or "unknown"

    # Prefer the executed result's status; fall back to the manifest's.
    execution_status = (
        _get_str(execution_result, "execution_status")
        or _get_str(execution_manifest, "execution_status")
        or "unknown"
    )

    review_required: bool | None = None
    if isinstance(effective_policy, dict) and isinstance(
        effective_policy.get("review_required"), bool
    ):
        review_required = effective_policy["review_required"]

    blocked_by_review = execution_status == "blocked" and review_required is True

    return {
        "run_dir": str(run_path),
        "complete_safe_noop_run": inspection["complete_safe_noop_run"],
        "artifacts": inspection["artifacts"],
        "candidate_dir_present": (run_path / "candidate").exists(),
        "compilation_status": compilation_status,
        "execution_status": execution_status,
        "review_required": review_required,
        "blocked_by_review": blocked_by_review,
        "candidate_workflow": _extract_candidate_workflow(run_path),
        "status_command": (
            f"python -m cli.run_status_cli --run-dir {run_path} --view"
        ),
    }
