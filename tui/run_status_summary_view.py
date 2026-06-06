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

    status_command = summary.get("status_command")
    if status_command:
        lines.append("")
        lines.append(f"status command: {status_command}")

    return "\n".join(lines)
