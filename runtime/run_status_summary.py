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
UNSUPPORTED_AUTHORITY_DIAGNOSTIC_CODES = frozenset(
    (
        "UNSUPPORTED_SECRET_FIELD",
        "UNSUPPORTED_CAPABILITY_ENVELOPE",
        "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
        "UNSUPPORTED_AUTHORITY_ARTIFACT",
        "UNSUPPORTED_EXECUTION_BINDING",
    )
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


def _extract_operator_review_notes(
    run_path: Path,
    candidate_workflow: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return display-only operator-authored notes for known candidate nodes only.

    Reads ``<run-dir>/candidate/OperatorReviewNotes.json`` fail-soft. This is a
    local operator/demo input only: not a control-plane artifact, not compiler
    input, not approval data, and not authority. Only notes for node IDs already
    present in the display-only candidate workflow are surfaced.
    """

    if not isinstance(candidate_workflow, dict):
        return None

    raw_nodes = candidate_workflow.get("nodes")
    if not isinstance(raw_nodes, list):
        return None

    known_node_ids = {
        node_id
        for node in raw_nodes
        if isinstance(node, dict)
        for node_id in [_get_str(node, "node_id")]
        if node_id is not None
    }
    if not known_node_ids:
        return None

    notes_path = run_path / "candidate" / "OperatorReviewNotes.json"
    review_notes = _safe_load_json(notes_path)
    if not isinstance(review_notes, dict):
        return None

    raw_notes = review_notes.get("notes")
    if not isinstance(raw_notes, list):
        return None

    notes_by_node: dict[str, list[dict[str, str]]] = {}
    note_count = 0
    for raw_note in raw_notes:
        node_id = _get_str(raw_note, "node_id")
        if node_id is None or node_id not in known_node_ids:
            continue

        display_note = {
            field_name: field_value
            for field_name in ("note_type", "note", "requested_action", "reviewer")
            for field_value in [_get_str(raw_note, field_name)]
            if field_value is not None
        }
        if not display_note:
            continue

        notes_by_node.setdefault(node_id, []).append(display_note)
        note_count += 1

    if not notes_by_node:
        return None

    extracted_notes: dict[str, Any] = {
        "display_only": True,
        "operator_authored": True,
        "not_authority": True,
        "not_approval": True,
        "not_compiler_input": True,
        "not_control_plane_artifact": True,
        "current_run_scope_only": True,
        "notes_path": str(notes_path),
        "note_count": note_count,
        "notes_by_node": notes_by_node,
    }

    workflow_id = _get_str(review_notes, "workflow_id")
    if workflow_id is not None:
        extracted_notes["workflow_id"] = workflow_id

    workflow_revision_id = _get_str(review_notes, "workflow_revision_id")
    if workflow_revision_id is not None:
        extracted_notes["workflow_revision_id"] = workflow_revision_id

    return extracted_notes


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


def _build_authority_projection_entries(effective_policy: Any) -> list[str]:
    if not isinstance(effective_policy, dict):
        return []

    entries: list[str] = []

    allowed_tools = effective_policy.get("allowed_tools")
    if isinstance(allowed_tools, list):
        for tool in allowed_tools:
            tool_name = _get_str(tool, "tool_name")
            if tool_name is None:
                continue
            access_mode = _get_str(tool, "access_mode")
            suffix = f" access_mode={access_mode}" if access_mode is not None else ""
            entries.append(f"tool: {tool_name}{suffix}")

    allowed_connectors = effective_policy.get("allowed_connectors")
    if isinstance(allowed_connectors, list):
        for connector in allowed_connectors:
            connector_name = _get_str(connector, "connector_name")
            if connector_name is None:
                continue
            scope = _get_str(connector, "scope")
            suffix = f" scope={scope}" if scope is not None else ""
            entries.append(f"connector: {connector_name}{suffix}")

    allowed_permissions = effective_policy.get("allowed_permissions")
    if isinstance(allowed_permissions, list):
        for permission_entry in allowed_permissions:
            permission = _get_str(permission_entry, "permission")
            target = _get_str(permission_entry, "target")
            if permission is None:
                continue
            suffix = f" target={target}" if target is not None else ""
            entries.append(f"permission: {permission}{suffix}")

    return entries


def _build_unsupported_authority_entries(compilation_report: Any) -> list[str]:
    if not isinstance(compilation_report, dict):
        return []

    diagnostics = compilation_report.get("diagnostics")
    if not isinstance(diagnostics, list):
        return []

    entries: list[str] = []
    for diagnostic in diagnostics:
        error_code = _get_str(diagnostic, "error_code")
        if error_code is None or error_code not in UNSUPPORTED_AUTHORITY_DIAGNOSTIC_CODES:
            continue

        artifact = _get_str(diagnostic, "artifact")
        path = _get_str(diagnostic, "path")
        detail_parts = [error_code]
        if artifact is not None:
            detail_parts.append(f"artifact={artifact}")
        if path is not None:
            detail_parts.append(f"path={path}")
        entries.append(" ".join(detail_parts))

    return entries


def _build_compiler_authorization_projection(
    candidate_workflow: dict[str, Any] | None,
    effective_policy: Any,
    compilation_report: Any,
    review_required: bool | None,
    blocked_by_review: bool,
) -> dict[str, Any] | None:
    """Return a display-only compiler authorization projection for blocked innovation_review runs."""

    workflow_id = _get_str(candidate_workflow, "workflow_id")
    if workflow_id is None or not workflow_id.startswith(
        INNOVATION_REVIEW_WORKFLOW_PREFIX
    ):
        return None

    if review_required is not True or not blocked_by_review:
        return None

    requested_authority = _build_authority_projection_entries(effective_policy)
    approval_required = list(requested_authority)
    blocked_authority = list(requested_authority)
    unsupported_authority = _build_unsupported_authority_entries(compilation_report)

    return {
        "display_only": True,
        "compiler_owned_summary": True,
        "not_executable": True,
        "not_persisted_as_artifact": True,
        "no_runtime_authority": True,
        "current_run_scope_only": True,
        "requested_authority": requested_authority,
        "approval_required": approval_required,
        "blocked_authority": blocked_authority,
        "unsupported_authority": unsupported_authority,
    }


def _build_unsupported_approval_binding_entries(compilation_report: Any) -> list[str]:
    if not isinstance(compilation_report, dict):
        return []

    diagnostics = compilation_report.get("diagnostics")
    if not isinstance(diagnostics, list):
        return []

    entries: list[str] = []
    for diagnostic in diagnostics:
        error_code = _get_str(diagnostic, "error_code")
        if error_code != "UNSUPPORTED_APPROVAL_BINDING":
            continue

        artifact = _get_str(diagnostic, "artifact")
        path = _get_str(diagnostic, "path")
        detail_parts = [error_code]
        if artifact is not None:
            detail_parts.append(f"artifact={artifact}")
        if path is not None:
            detail_parts.append(f"path={path}")
        entries.append(" ".join(detail_parts))

    return entries


def _build_approval_binding_summary(
    run_path: Path,
    candidate_workflow: dict[str, Any] | None,
    compilation_report: Any,
    review_required: bool | None,
    blocked_by_review: bool,
    compiler_authorization_projection: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return a display-only approval-binding summary for blocked innovation_review runs.

    This explains, for the current blocked request only, what an approval would
    bind to. It is derived entirely from already-read local run data: the
    candidate workflow identity, the local ``candidate/ApprovalRequests.json``
    proposal (read fail-soft, the same artifact the Review Gate already reads),
    the already-read ``CompilationReport.json`` diagnostics, and the already-built
    compiler authorization projection. It changes no approval resolution or
    matching behavior, implements no real approval binding, grants no authority,
    and writes nothing.
    """

    workflow_id = _get_str(candidate_workflow, "workflow_id")
    if workflow_id is None or not workflow_id.startswith(
        INNOVATION_REVIEW_WORKFLOW_PREFIX
    ):
        return None

    if review_required is not True or not blocked_by_review:
        return None

    # Whether an approval could bind to a candidate artifact revision and to a
    # requested-authority shape is reported as a fact derived only from data the
    # summary already holds; unknown when that data is unavailable.
    has_candidate_revision = (
        _get_str(candidate_workflow, "workflow_revision_id") is not None
    )
    binds_to_candidate_artifact: Any = True if has_candidate_revision else "unknown"

    requested_authority: list[Any] = []
    if isinstance(compiler_authorization_projection, dict):
        projected = compiler_authorization_projection.get("requested_authority")
        if isinstance(projected, list):
            requested_authority = projected
    binds_to_requested_authority: Any = True if requested_authority else "unknown"

    approval_subjects: list[dict[str, Any]] = []
    approval_requests = _safe_load_json(
        run_path / "candidate" / "ApprovalRequests.json"
    )
    if isinstance(approval_requests, dict):
        raw_requests = approval_requests.get("requests")
        if isinstance(raw_requests, list):
            for raw_request in raw_requests:
                if not isinstance(raw_request, dict):
                    continue
                approval_subjects.append(
                    {
                        "request_id": _get_str(raw_request, "request_id")
                        or "unknown",
                        "node_id": _get_str(raw_request, "node_id") or "unknown",
                        "approval_subject_hash": _get_str(
                            raw_request, "approval_subject_hash"
                        )
                        or "unknown",
                        "binds_to_current_request": True,
                        "binds_to_candidate_artifact": binds_to_candidate_artifact,
                        "binds_to_requested_authority": binds_to_requested_authority,
                    }
                )

    return {
        "display_only": True,
        "operator_owned": True,
        "not_reusable_authority": True,
        "no_approval_carryover": True,
        "no_runtime_authority": True,
        "current_run_scope_only": True,
        "current_request_scope_only": True,
        "approval_subjects": approval_subjects,
        "unsupported_binding_claims": _build_unsupported_approval_binding_entries(
            compilation_report
        ),
    }


def _artifact_presence_status(value: Any, path: Path) -> str:
    """Fail-soft presence status: present (parsed), unknown (exists but
    unreadable/malformed), or missing."""

    if isinstance(value, dict):
        return "present"
    if path.exists():
        return "unknown"
    return "missing"


def _list_field_len(value: Any, key: str) -> int:
    if isinstance(value, dict):
        items = value.get(key)
        if isinstance(items, list):
            return len(items)
    return 0


def _build_verifier_evidence_status(
    run_path: Path,
    candidate_workflow: dict[str, Any] | None,
    execution_manifest: Any,
    execution_result: Any,
    review_required: bool | None,
    blocked_by_review: bool,
) -> dict[str, Any] | None:
    """Return a display-only verifier/evidence status for blocked innovation_review runs.

    This is a read-only reporting section, not a verifier and not evidence
    generation. It reports only the presence of local run artifacts already part
    of the run/status model (``ExecutionManifest.json``, ``ExecutionResult.json``,
    ``AuditLog.jsonl``) and the existing safe no-op produced-evidence/side-effect
    counts. It writes nothing, generates no ``EvidenceLineage.json`` or
    ``VerifierOutput.json``, reads no future fixtures, and grants no authority.
    """

    workflow_id = _get_str(candidate_workflow, "workflow_id")
    if workflow_id is None or not workflow_id.startswith(
        INNOVATION_REVIEW_WORKFLOW_PREFIX
    ):
        return None

    if review_required is not True or not blocked_by_review:
        return None

    # Counts reflect the existing safe no-op result; the executed result is
    # preferred, falling back to the manifest, defaulting to zero.
    count_source: Any = (
        execution_result if isinstance(execution_result, dict) else execution_manifest
    )

    return {
        "display_only": True,
        "reporting_only": True,
        "not_authority": True,
        "not_verifier_output_artifact": True,
        "not_evidence_lineage_artifact": True,
        "no_runtime_authority": True,
        "no_execution": True,
        "no_approval": True,
        "current_run_scope_only": True,
        "manifest_status": _artifact_presence_status(
            execution_manifest, run_path / "ExecutionManifest.json"
        ),
        "execution_result_status": _artifact_presence_status(
            execution_result, run_path / "ExecutionResult.json"
        ),
        "audit_log_status": (
            "present" if (run_path / "AuditLog.jsonl").exists() else "missing"
        ),
        "produced_evidence_count": _list_field_len(count_source, "produced_evidence"),
        "side_effect_count": _list_field_len(count_source, "side_effects"),
        "verification_status": "not_implemented",
        "findings": [
            "V1 safe no-op reports artifact presence only; no verifier behavior "
            "is implemented."
        ],
    }


def _build_broker_boundary_status(
    candidate_workflow: dict[str, Any] | None,
    review_required: bool | None,
    blocked_by_review: bool,
) -> dict[str, Any] | None:
    """Return a display-only broker boundary status for blocked innovation_review runs.

    This is a read-only reporting section, not a broker, not a fake/no-op broker
    interface, and not a sandbox. It reports only that V1 safe no-op has no
    broker or sandbox implementation and generates no broker artifacts. It writes
    nothing, generates no ``BrokerRequest.json`` / ``BrokerDecision.json`` /
    ``BrokerResult.json``, reads no future fixtures, and grants no authority.
    """

    workflow_id = _get_str(candidate_workflow, "workflow_id")
    if workflow_id is None or not workflow_id.startswith(
        INNOVATION_REVIEW_WORKFLOW_PREFIX
    ):
        return None

    if review_required is not True or not blocked_by_review:
        return None

    return {
        "display_only": True,
        "reporting_only": True,
        "not_authority": True,
        "not_broker_request_artifact": True,
        "not_broker_decision_artifact": True,
        "not_broker_result_artifact": True,
        "no_broker_implementation": True,
        "no_sandbox_implementation": True,
        "no_runtime_authority": True,
        "no_execution": True,
        "no_approval": True,
        "current_run_scope_only": True,
        "broker_request_status": "not_generated",
        "broker_decision_status": "not_generated",
        "broker_result_status": "not_generated",
        "sandbox_status": "not_implemented",
        "execution_status": "safe_noop_only",
        "findings": [
            "V1 safe no-op has no broker or sandbox implementation; no broker "
            "artifacts are generated."
        ],
    }


def _build_operator_review_packet(
    review_required: bool | None,
    blocked_by_review: bool,
    review_gate: dict[str, Any] | None,
    governance_readiness_checklist: list[dict[str, str]] | None,
    candidate_workflow: dict[str, Any] | None,
    operator_review_notes: dict[str, Any] | None,
    fixture_lineage: dict[str, Any] | None,
    proposed_tool_access: dict[str, Any] | None,
    compiler_authorization_projection: dict[str, Any] | None,
    approval_binding_summary: dict[str, Any] | None,
    verifier_evidence_status: dict[str, Any] | None,
    broker_boundary_status: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return a display-only operator review checklist for blocked runs only."""

    if review_required is not True or not blocked_by_review:
        return None

    included_sections: list[str] = []
    if review_gate is not None:
        included_sections.append("Review Gate")
    if governance_readiness_checklist is not None:
        included_sections.append("Governance Readiness Checklist")
    if candidate_workflow is not None:
        included_sections.append("Candidate Workflow")
    if operator_review_notes is not None:
        included_sections.append("Operator Review Notes")
    if fixture_lineage is not None:
        included_sections.append("Fixture Lineage")
    if proposed_tool_access is not None:
        included_sections.append("Proposed Tool Access")
    if compiler_authorization_projection is not None:
        included_sections.append("Compiler Authorization Projection")
    if approval_binding_summary is not None:
        included_sections.append("Approval Binding Summary")
    if verifier_evidence_status is not None:
        included_sections.append("Verifier / Evidence Status")
    if broker_boundary_status is not None:
        included_sections.append("Broker Boundary Status")

    return {
        "review_required": True,
        "blocked_by_review": True,
        "decision_scope": "current run/request only",
        "execution_mode": "safe_noop_only",
        "included_sections": included_sections,
    }


def _build_governance_readiness_checklist(
    compilation_status: str,
    review_required: bool | None,
    blocked_by_review: bool,
    governance_lifecycle_stage: dict[str, Any],
    review_gate: dict[str, Any] | None,
    approval_binding_summary: dict[str, Any] | None,
    verifier_evidence_status: dict[str, Any] | None,
    broker_boundary_status: dict[str, Any] | None,
) -> list[dict[str, str]] | None:
    """Return a display-only readiness checklist derived from summary fields only."""

    lifecycle_stage = _get_str(governance_lifecycle_stage, "stage")
    if lifecycle_stage not in {
        "blocked_awaiting_operator_approval",
        "compile_failed",
        "completed_safe_noop",
        "compiled_no_review_required",
    }:
        return None

    checklist: list[dict[str, str]] = []

    if compilation_status == "compiled":
        checklist.append(
            {
                "label": "Compiler static validation",
                "status": "satisfied",
                "reason": "Compilation status is compiled.",
            }
        )
    elif compilation_status == "failed":
        checklist.append(
            {
                "label": "Compiler static validation",
                "status": "blocked",
                "reason": "Compilation status is failed; the proposal was not authorized.",
            }
        )
    else:
        checklist.append(
            {
                "label": "Compiler static validation",
                "status": "missing",
                "reason": (
                    "Compilation status is unknown from the available run artifacts."
                ),
            }
        )

    if blocked_by_review and review_required is True:
        reason = _get_str(review_gate, "guidance") or (
            "Review is required and the run remains blocked pending a "
            "current-run approval decision."
        )
        checklist.append(
            {
                "label": "Operator approval gate",
                "status": "missing",
                "reason": reason,
            }
        )
    elif review_required is False:
        checklist.append(
            {
                "label": "Operator approval gate",
                "status": "satisfied",
                "reason": "Review is not required for this run/request.",
            }
        )

    lifecycle_status = {
        "blocked_awaiting_operator_approval": "blocked",
        "compile_failed": "blocked",
        "completed_safe_noop": "inspect-only",
        "compiled_no_review_required": "satisfied",
        "unknown": "missing",
    }.get(lifecycle_stage or "unknown", "missing")
    lifecycle_reason = _get_str(
        governance_lifecycle_stage, "next_operator_action"
    ) or (
        "The governance lifecycle stage could not be determined from the "
        "available summary fields."
    )
    checklist.append(
        {
            "label": "Governance lifecycle stage",
            "status": lifecycle_status,
            "reason": lifecycle_reason,
        }
    )

    execution_mode = _get_str(governance_lifecycle_stage, "execution_mode")
    if execution_mode is not None:
        checklist.append(
            {
                "label": "Safe no-op execution posture",
                "status": "inspect-only" if execution_mode == "safe_noop_only" else "missing",
                "reason": (
                    "Execution mode is safe_noop_only; the run is safe to inspect only."
                    if execution_mode == "safe_noop_only"
                    else f"Execution mode is {execution_mode}."
                ),
            }
        )

    if isinstance(approval_binding_summary, dict):
        binding_flags = (
            approval_binding_summary.get("current_run_scope_only") is True
            and approval_binding_summary.get("current_request_scope_only") is True
            and approval_binding_summary.get("no_approval_carryover") is True
            and approval_binding_summary.get("not_reusable_authority") is True
        )
        checklist.append(
            {
                "label": "Approval binding scope",
                "status": "satisfied" if binding_flags else "missing",
                "reason": (
                    "Any approval remains current run/request only; no approval "
                    "carryover or reusable authority is reported."
                    if binding_flags
                    else (
                        "Approval binding scope could not be confirmed from the "
                        "available summary fields."
                    )
                ),
            }
        )

    if isinstance(verifier_evidence_status, dict):
        reason = "Verification status is unknown."
        findings = verifier_evidence_status.get("findings")
        if isinstance(findings, list):
            for finding in findings:
                if isinstance(finding, str):
                    reason = finding
                    break
        checklist.append(
            {
                "label": "Verifier / evidence status",
                "status": (
                    "inspect-only"
                    if _get_str(verifier_evidence_status, "verification_status")
                    == "not_implemented"
                    else "missing"
                ),
                "reason": reason,
            }
        )

    if isinstance(broker_boundary_status, dict):
        reason = "Broker boundary status is unknown."
        findings = broker_boundary_status.get("findings")
        if isinstance(findings, list):
            for finding in findings:
                if isinstance(finding, str):
                    reason = finding
                    break
        checklist.append(
            {
                "label": "Broker / sandbox boundary",
                "status": (
                    "inspect-only"
                    if broker_boundary_status.get("no_broker_implementation") is True
                    and broker_boundary_status.get("no_sandbox_implementation") is True
                    else "missing"
                ),
                "reason": reason,
            }
        )

    return checklist


def _build_governance_lifecycle_stage(
    compilation_status: str,
    execution_status: str,
    review_required: bool | None,
    blocked_by_review: bool,
) -> dict[str, Any]:
    """Return a display-only governance lifecycle stage projection.

    Derived only from already-computed status fields (no new artifact reads). It
    maps the run onto the governed workflow flow (planner proposal -> compiler
    authorization -> operator approval -> safe no-op run -> reporting) and states
    the next safe operator action. It is display-only: it creates no authority,
    approval, evidence, execution capability, or runtime behavior, and the stage
    itself is not authoritative.
    """

    if compilation_status == "failed":
        stage = "compile_failed"
        next_operator_action = (
            "review compiler diagnostics; the proposal was not authorized and "
            "nothing was executed"
        )
    elif blocked_by_review:
        stage = "blocked_awaiting_operator_approval"
        next_operator_action = (
            "review and approve or deny requested access for the current "
            "run/request"
        )
    elif execution_status == "completed":
        stage = "completed_safe_noop"
        next_operator_action = (
            "inspect status/audit output; no real execution was performed"
        )
    elif compilation_status == "compiled" and review_required is False:
        stage = "compiled_no_review_required"
        next_operator_action = (
            "proceed to the safe no-op run; no operator approval is required for "
            "this run/request"
        )
    else:
        stage = "unknown"
        next_operator_action = (
            "inspect run-status output; the lifecycle stage could not be "
            "determined from the available run artifacts"
        )

    return {
        "stage": stage,
        "next_operator_action": next_operator_action,
        "authority_boundary": (
            "compiler-owned authorization only; planner is non-authoritative"
        ),
        "approval_scope": "current run/request only",
        "execution_mode": "safe_noop_only",
        "display_only": True,
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
    operator_review_notes = _extract_operator_review_notes(
        run_path,
        candidate_workflow,
    )
    fixture_lineage = _extract_fixture_lineage(candidate_workflow)
    proposed_tool_access = _extract_proposed_tool_access(run_path, candidate_workflow)
    compiler_authorization_projection = _build_compiler_authorization_projection(
        candidate_workflow,
        effective_policy,
        compilation_report,
        review_required,
        blocked_by_review,
    )
    approval_binding_summary = _build_approval_binding_summary(
        run_path,
        candidate_workflow,
        compilation_report,
        review_required,
        blocked_by_review,
        compiler_authorization_projection,
    )
    verifier_evidence_status = _build_verifier_evidence_status(
        run_path,
        candidate_workflow,
        execution_manifest,
        execution_result,
        review_required,
        blocked_by_review,
    )
    broker_boundary_status = _build_broker_boundary_status(
        candidate_workflow,
        review_required,
        blocked_by_review,
    )
    governance_lifecycle_stage = _build_governance_lifecycle_stage(
        compilation_status,
        execution_status,
        review_required,
        blocked_by_review,
    )
    governance_readiness_checklist = _build_governance_readiness_checklist(
        compilation_status,
        review_required,
        blocked_by_review,
        governance_lifecycle_stage,
        review_gate,
        approval_binding_summary,
        verifier_evidence_status,
        broker_boundary_status,
    )

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
        "governance_lifecycle_stage": governance_lifecycle_stage,
        "governance_readiness_checklist": governance_readiness_checklist,
        "candidate_workflow": candidate_workflow,
        "operator_review_notes": operator_review_notes,
        "fixture_lineage": fixture_lineage,
        "proposed_tool_access": proposed_tool_access,
        "compiler_authorization_projection": compiler_authorization_projection,
        "approval_binding_summary": approval_binding_summary,
        "verifier_evidence_status": verifier_evidence_status,
        "broker_boundary_status": broker_boundary_status,
        "operator_review_packet": _build_operator_review_packet(
            review_required,
            blocked_by_review,
            review_gate,
            governance_readiness_checklist,
            candidate_workflow,
            operator_review_notes,
            fixture_lineage,
            proposed_tool_access,
            compiler_authorization_projection,
            approval_binding_summary,
            verifier_evidence_status,
            broker_boundary_status,
        ),
        "status_command": (
            f"python -m cli.run_status_cli --run-dir {run_path} --view"
        ),
    }
