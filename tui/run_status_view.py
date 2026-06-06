from __future__ import annotations

from typing import Any, Mapping


def _bool_text(value: Any) -> str:
    return "true" if value is True else "false"


def build_run_status_view_model(status: Mapping[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    artifacts = status.get("artifacts", {})
    if isinstance(artifacts, Mapping):
        for artifact_name, artifact_status in artifacts.items():
            exists = False
            if isinstance(artifact_status, Mapping):
                exists = artifact_status.get("exists") is True
            rows.append(
                {
                    "artifact": artifact_name,
                    "exists": exists,
                    "marker": "[x]" if exists else "[ ]",
                }
            )

    return {
        "title": "Safe No-Op Run Status",
        "run_dir": str(status.get("run_dir", "")),
        "complete_safe_noop_run": status.get("complete_safe_noop_run") is True,
        "rows": rows,
    }


def render_run_status_view(status: Mapping[str, Any]) -> str:
    view_model = build_run_status_view_model(status)
    lines = [
        view_model["title"],
        f"run_dir: {view_model['run_dir']}",
        "complete_safe_noop_run: "
        f"{_bool_text(view_model['complete_safe_noop_run'])}",
        "",
    ]
    for row in view_model["rows"]:
        lines.append(f"{row['marker']} {row['artifact']}")
    return "\n".join(lines)
