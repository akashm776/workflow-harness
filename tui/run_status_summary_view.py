"""Dependency-free text renderer for the read-only run summary.

Pure renderer: it does not mutate its input and performs no I/O. It only formats
the dict produced by ``runtime.run_status_summary.summarize_run_directory``.
"""

from __future__ import annotations

from typing import Any, Mapping


def _bool_text(value: Any) -> str:
    return "true" if value is True else "false"


def _field_text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def render_run_status_summary_view(summary: Mapping[str, Any]) -> str:
    lines = [
        "Safe No-Op Run Summary",
        f"run_dir: {summary.get('run_dir', '')}",
        f"complete_safe_noop_run: {_bool_text(summary.get('complete_safe_noop_run'))}",
        f"compilation_status: {_field_text(summary.get('compilation_status'))}",
        f"execution_status: {_field_text(summary.get('execution_status'))}",
        f"review_required: {_field_text(summary.get('review_required'))}",
        f"blocked_by_review: {_bool_text(summary.get('blocked_by_review'))}",
        f"candidate_dir_present: {_bool_text(summary.get('candidate_dir_present'))}",
        "",
    ]

    artifacts = summary.get("artifacts", {})
    if isinstance(artifacts, Mapping):
        for artifact_name, artifact_status in artifacts.items():
            exists = False
            if isinstance(artifact_status, Mapping):
                exists = artifact_status.get("exists") is True
            marker = "[x]" if exists else "[ ]"
            lines.append(f"{marker} {artifact_name}")

    review_gate_lines = _review_gate_lines(
        summary.get("review_gate"),
        summary.get("approval_request_count"),
    )
    if review_gate_lines:
        lines.append("")
        lines.extend(review_gate_lines)

    candidate_lines = _candidate_workflow_lines(summary.get("candidate_workflow"))
    if candidate_lines:
        lines.append("")
        lines.extend(candidate_lines)

    status_command = summary.get("status_command")
    if status_command:
        lines.append("")
        lines.append(f"status command: {status_command}")

    return "\n".join(lines)


def _review_gate_lines(review_gate: Any, approval_request_count: Any) -> list[str]:
    if not isinstance(review_gate, Mapping):
        return []

    lines = ["Review Gate:"]

    blocked_reason = review_gate.get("blocked_reason")
    if blocked_reason is not None:
        lines.append(f"blocked_reason: {blocked_reason}")

    if isinstance(approval_request_count, int):
        lines.append(f"approval_request_count: {approval_request_count}")

    request_id = review_gate.get("request_id")
    if isinstance(request_id, str):
        lines.append(f"approval_request_id: {request_id}")

    node_id = review_gate.get("node_id")
    if isinstance(node_id, str):
        lines.append(f"node_id: {node_id}")

    reason = review_gate.get("reason")
    if isinstance(reason, str):
        lines.append(f"reason: {reason}")

    approval_requests_path = review_gate.get("approval_requests_path")
    if isinstance(approval_requests_path, str):
        lines.append(f"approval request artifact: {approval_requests_path}")

    lines.append(
        "unblock: supply a matching ApprovalDecisions.json for this run/request only"
    )
    return lines


def _candidate_workflow_lines(candidate_workflow: Any) -> list[str]:
    if not isinstance(candidate_workflow, Mapping):
        return []
    nodes = candidate_workflow.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return []

    edges = candidate_workflow.get("edges")
    outgoing: dict[str, list[str]] = {}
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, Mapping):
                continue
            from_node_id = edge.get("from_node_id")
            to_node_id = edge.get("to_node_id")
            if isinstance(from_node_id, str) and isinstance(to_node_id, str):
                outgoing.setdefault(from_node_id, []).append(to_node_id)

    lines = ["Candidate Workflow:"]
    for node in nodes:
        if not isinstance(node, Mapping):
            continue
        node_id = node.get("node_id")
        node_type = node.get("node_type")
        if not isinstance(node_id, str) or not isinstance(node_type, str):
            continue
        display_name = node.get("display_name")
        suffix = f" {display_name}" if isinstance(display_name, str) else ""
        lines.append(f"- {node_id} [{node_type}]{suffix}")
        for to_node_id in outgoing.get(node_id, []):
            lines.append(f"  -> {to_node_id}")
    return lines
