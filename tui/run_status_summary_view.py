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

    candidate_lines = _candidate_workflow_lines(summary.get("candidate_workflow"))
    if candidate_lines:
        lines.append("")
        lines.extend(candidate_lines)

    status_command = summary.get("status_command")
    if status_command:
        lines.append("")
        lines.append(f"status command: {status_command}")

    return "\n".join(lines)


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
