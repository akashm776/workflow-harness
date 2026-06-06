from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from compiler.approval_resolution import resolve_review_required


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _copy_object_list(values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not values:
        return []
    return [dict(value) for value in values]


def build_effective_policy(
    workflow_spec_path: str | Path,
    requested_auth_path: str | Path,
    node_type_registry_path: str | Path,
    approval_decisions_path: str | Path | None = None,
    approval_requests_path: str | Path | None = None,
) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)
    requested_auth = _load_json(requested_auth_path)
    node_type_registry = _load_json(node_type_registry_path)

    requested_node_id = requested_auth["node_id"]
    requested_node = next(
        (
            node
            for node in workflow_spec.get("nodes", [])
            if node.get("node_id") == requested_node_id
        ),
        None,
    )
    if requested_node is None:
        raise ValueError(f"requested node_id not found in WorkflowSpec: {requested_node_id}")

    registered_node_types = {
        entry["node_type"]
        for entry in node_type_registry.get("node_types", [])
        if "node_type" in entry
    }
    if requested_node.get("node_type") not in registered_node_types:
        raise ValueError(
            "requested node_id references unregistered node_type: "
            f"{requested_node.get('node_type')}"
        )

    requested_tools = _copy_object_list(requested_auth.get("requested_tools"))
    requested_connectors = _copy_object_list(requested_auth.get("requested_connectors"))
    requested_permissions = _copy_object_list(requested_auth.get("requested_permissions"))
    review_required = bool(
        requested_tools or requested_connectors or requested_permissions
    )

    if review_required and approval_decisions_path is not None:
        approval_decisions = _load_json(approval_decisions_path)
        if approval_requests_path is not None:
            approval_requests = _load_json(approval_requests_path)
            matching_request = next(
                (
                    request
                    for request in approval_requests.get("requests", [])
                    if request.get("node_id") == requested_node_id
                ),
                None,
            )
            if matching_request is not None:
                request_id = matching_request.get("request_id")
                approval_subject_hash = matching_request.get("approval_subject_hash")
                if (
                    isinstance(request_id, str)
                    and request_id
                    and isinstance(approval_subject_hash, str)
                    and approval_subject_hash
                ):
                    normalized_approval_decisions = {
                        "decisions": [],
                    }
                    for decision_entry in approval_decisions.get("decisions", []):
                        if not isinstance(decision_entry, dict):
                            continue
                        normalized_decision_entry = dict(decision_entry)
                        if normalized_decision_entry.get("request_id") == request_id:
                            normalized_decision_entry.setdefault("node_id", requested_node_id)
                            normalized_decision_entry.setdefault(
                                "approval_subject_hash", approval_subject_hash
                            )
                        normalized_approval_decisions["decisions"].append(
                            normalized_decision_entry
                        )

                    review_required = resolve_review_required(
                        node_id=requested_node_id,
                        approval_subject_hash=approval_subject_hash,
                        approval_decisions=normalized_approval_decisions,
                    )

    return {
        "schema_version": "m1",
        "node_id": requested_node_id,
        "workflow_revision_id": workflow_spec["workflow_revision_id"],
        "policy_bundle_digest": workflow_spec["policy_bundle_digest"],
        "artifact_lifecycle_state": "compiled",
        "allowed_tools": requested_tools,
        "allowed_connectors": requested_connectors,
        "allowed_permissions": requested_permissions,
        "review_required": review_required,
    }
