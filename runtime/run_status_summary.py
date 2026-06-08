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


INNOVATION_REVIEW_WORKFLOW_PREFIX = "planner-innovation-review-workflow-"
INNOVATION_CONTEXT_FIXTURE_PATHS = (
    "fixtures/future/innovation-context/ProgramContext.json",
    "fixtures/future/innovation-context/RepoContextSummary.json",
    "fixtures/future/innovation-context/ConfluenceContextSummary.json",
    "fixtures/future/innovation-context/IssueTrackerContextSummary.json",
    "fixtures/future/innovation-context/Rubric.json",
)


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


def _extract_review_gate(
    run_path: Path,
    blocked_by_review: bool,
) -> tuple[bool, int, str | None, dict[str, Any] | None]:
    approval_requests_path = run_path / "candidate" / "ApprovalRequests.json"
    approval_requests_present = approval_requests_path.exists()
    approval_requests_path_text = (
        str(approval_requests_path) if approval_requests_present else None
    )
    approval_request_count = 0

    review_gate: dict[str, Any] | None = None
    if blocked_by_review:
        review_gate = {
            "blocked_reason": "review_required",
            "guidance": (
                "Explicit current-run approval is required to unblock this "
                "safe no-op run."
            ),
            "approval_requests_path": approval_requests_path_text,
        }

    approval_requests = _safe_load_json(approval_requests_path)
    if not isinstance(approval_requests, dict):
        return (
            approval_requests_present,
            approval_request_count,
            approval_requests_path_text,
            review_gate,
        )

    raw_requests = approval_requests.get("requests")
    if not isinstance(raw_requests, list):
        return (
            approval_requests_present,
            approval_request_count,
            approval_requests_path_text,
            review_gate,
        )

    approval_request_count = len(raw_requests)
    if review_gate is None:
        return (
            approval_requests_present,
            approval_request_count,
            approval_requests_path_text,
            review_gate,
        )

    for raw_request in raw_requests:
        if not isinstance(raw_request, dict):
            continue
        request_id = _get_str(raw_request, "request_id")
        node_id = _get_str(raw_request, "node_id")
        reason = _get_str(raw_request, "reason")
        if request_id is not None:
            review_gate["request_id"] = request_id
        if node_id is not None:
            review_gate["node_id"] = node_id
        if reason is not None:
            review_gate["reason"] = reason
        break

    return (
        approval_requests_present,
        approval_request_count,
        approval_requests_path_text,
        review_gate,
    )


def _extract_fixture_lineage(
    candidate_workflow: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return display-only future fixture lineage for innovation_review only.

    This is operator-facing metadata derived from already-read candidate
    workflow fields. It is not validation, authority, execution eligibility, or
    fixture loading. The fixture paths remain inert strings only.
    """

    workflow_id = _get_str(candidate_workflow, "workflow_id")
    if workflow_id is None or not workflow_id.startswith(
        INNOVATION_REVIEW_WORKFLOW_PREFIX
    ):
        return None

    return {
        "display_only": True,
        "not_loaded": True,
        "not_control_plane_inputs": True,
        "paths": list(INNOVATION_CONTEXT_FIXTURE_PATHS),
    }


def _extract_proposed_tool_access(
    run_path: Path,
    candidate_workflow: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return display-only proposed tool access for innovation_review only.

    This reads the local candidate RequestedAuth proposal fail-soft. It remains
    proposal metadata only: no tool execution, no connector support, no
    approval semantics, and no authority.
    """

    workflow_id = _get_str(candidate_workflow, "workflow_id")
    if workflow_id is None or not workflow_id.startswith(
        INNOVATION_REVIEW_WORKFLOW_PREFIX
    ):
        return None

    requested_auth = _safe_load_json(run_path / "candidate" / "RequestedAuth.json")
    if not isinstance(requested_auth, dict):
        return None

    tools: list[dict[str, str]] = []
    raw_tools = requested_auth.get("requested_tools")
    if isinstance(raw_tools, list):
        for raw_tool in raw_tools:
            tool_name = _get_str(raw_tool, "tool_name")
            if tool_name is None:
                continue
            tool: dict[str, str] = {"tool_name": tool_name}
            access_mode = _get_str(raw_tool, "access_mode")
            if access_mode is not None:
                tool["access_mode"] = access_mode
            tools.append(tool)

    connectors: list[dict[str, str]] = []
    raw_connectors = requested_auth.get("requested_connectors")
    if isinstance(raw_connectors, list):
        for raw_connector in raw_connectors:
            connector_name = _get_str(raw_connector, "connector_name")
            scope = _get_str(raw_connector, "scope")
            if connector_name is None:
                continue
            connector: dict[str, str] = {"connector_name": connector_name}
            if scope is not None:
                connector["scope"] = scope
            connectors.append(connector)

    if not tools and not connectors:
        return None

    return {
        "display_only": True,
        "proposal_only": True,
        "no_execution": True,
        "no_connector_support": True,
        "tools": tools,
        "connectors": connectors,
    }


def _build_operator_review_packet(
    review_required: bool | None,
    blocked_by_review: bool,
    review_gate: dict[str, Any] | None,
    candidate_workflow: dict[str, Any] | None,
    fixture_lineage: dict[str, Any] | None,
    proposed_tool_access: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return a display-only operator review checklist for blocked runs only."""

    if review_required is not True or not blocked_by_review:
        return None

    included_sections: list[str] = []
    if review_gate is not None:
        included_sections.append("Review Gate")
    if candidate_workflow is not None:
        included_sections.append("Candidate Workflow")
    if fixture_lineage is not None:
        included_sections.append("Fixture Lineage")
    if proposed_tool_access is not None:
        included_sections.append("Proposed Tool Access")

    return {
        "review_required": True,
        "blocked_by_review": True,
        "decision_scope": "current run/request only",
        "execution_mode": "safe_noop_only",
        "included_sections": included_sections,
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
    (
        approval_requests_present,
        approval_request_count,
        approval_requests_path,
        review_gate,
    ) = _extract_review_gate(run_path, blocked_by_review)
    candidate_workflow = _extract_candidate_workflow(run_path)
    fixture_lineage = _extract_fixture_lineage(candidate_workflow)
    proposed_tool_access = _extract_proposed_tool_access(run_path, candidate_workflow)

    return {
        "run_dir": str(run_path),
        "complete_safe_noop_run": inspection["complete_safe_noop_run"],
        "artifacts": inspection["artifacts"],
        "candidate_dir_present": (run_path / "candidate").exists(),
        "compilation_status": compilation_status,
        "execution_status": execution_status,
        "review_required": review_required,
        "blocked_by_review": blocked_by_review,
        "approval_requests_present": approval_requests_present,
        "approval_request_count": approval_request_count,
        "approval_requests_path": approval_requests_path,
        "review_gate": review_gate,
        "candidate_workflow": candidate_workflow,
        "fixture_lineage": fixture_lineage,
        "proposed_tool_access": proposed_tool_access,
        "operator_review_packet": _build_operator_review_packet(
            review_required,
            blocked_by_review,
            review_gate,
            candidate_workflow,
            fixture_lineage,
            proposed_tool_access,
        ),
        "status_command": (
            f"python -m cli.run_status_cli --run-dir {run_path} --view"
        ),
    }
