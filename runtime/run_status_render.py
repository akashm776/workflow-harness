from __future__ import annotations

from typing import Any, Mapping


def _bool_text(value: Any) -> str:
    return "true" if value is True else "false"


def render_run_status_text(status: Mapping[str, Any]) -> str:
    lines = [
        f"run_dir: {status.get('run_dir', '')}",
        f"complete_safe_noop_run: {_bool_text(status.get('complete_safe_noop_run'))}",
    ]

    artifacts = status.get("artifacts", {})
    if isinstance(artifacts, Mapping):
        for artifact_name, artifact_status in artifacts.items():
            exists = False
            if isinstance(artifact_status, Mapping):
                exists = artifact_status.get("exists") is True
            marker = "[x]" if exists else "[ ]"
            lines.append(f"{marker} {artifact_name}")

    return "\n".join(lines)
