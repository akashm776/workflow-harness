from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from compiler.static_validation import validate_static_inputs


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_compilation_report(
    workflow_spec_path: str | Path,
    node_type_registry_path: str | Path,
    requested_auth_path: str | Path,
    approval_requests_path: str | Path,
    *,
    approval_decisions_path: str | Path | None = None,
) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)
    validation_result = validate_static_inputs(
        workflow_spec_path,
        node_type_registry_path,
        requested_auth_path,
        approval_requests_path,
        approval_decisions_path=approval_decisions_path,
    )

    report: dict[str, Any] = {
        "schema_version": "m1",
    }

    # Only copy identity fields when they are strings. If a disallowed float or
    # non-finite value is in one of these fields, omit it so the failed report
    # never re-emits the disallowed authority value.
    for field_name in (
        "graph_revision_id",
        "workflow_revision_id",
        "policy_bundle_digest",
    ):
        value = workflow_spec.get(field_name)
        if isinstance(value, str):
            report[field_name] = value

    if validation_result["ok"]:
        report["artifact_lifecycle_state"] = "compiled"
        report["status"] = "compiled"
        report["diagnostics"] = []
        return report

    report["artifact_lifecycle_state"] = "failed"
    report["status"] = "failed"
    report["diagnostics"] = validation_result["diagnostics"]
    return report
