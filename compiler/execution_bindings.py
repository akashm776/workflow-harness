from __future__ import annotations

from typing import Any, Mapping


def _copy_object_list(values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not values:
        return []
    return [dict(value) for value in values]


def build_execution_bindings(effective_policy: Mapping[str, Any]) -> dict[str, Any]:
    allowed_tools = _copy_object_list(effective_policy.get("allowed_tools"))
    allowed_connectors = _copy_object_list(effective_policy.get("allowed_connectors"))
    allowed_permissions = _copy_object_list(effective_policy.get("allowed_permissions"))

    bound_tools = [
        {
            **tool_entry,
            "binding_type": "builtin",
        }
        for tool_entry in allowed_tools
    ]
    bound_connectors = [
        {
            **connector_entry,
            "binding_ref": (
                f"connector-binding:{connector_entry['connector_name']}:"
                f"{connector_entry['scope']}"
            ),
        }
        for connector_entry in allowed_connectors
    ]
    bound_permissions = [
        {
            **permission_entry,
            "binding_ref": (
                f"permission-binding:{permission_entry['permission']}:"
                f"{permission_entry['target']}"
            ),
        }
        for permission_entry in allowed_permissions
    ]

    return {
        "schema_version": "m1",
        "node_id": effective_policy["node_id"],
        "workflow_revision_id": effective_policy["workflow_revision_id"],
        "policy_bundle_digest": effective_policy["policy_bundle_digest"],
        "artifact_lifecycle_state": "compiled",
        "bound_tools": bound_tools,
        "bound_connectors": bound_connectors,
        "bound_permissions": bound_permissions,
        "env_bindings": [],
    }
