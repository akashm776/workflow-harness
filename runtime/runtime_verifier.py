from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any, Mapping

from compiler.canonical_json import canonical_sha256_hex


def _artifact_entry_by_name(
    compiled_artifact_index: Mapping[str, Any], artifact_name: str
) -> Mapping[str, Any] | None:
    for artifact in compiled_artifact_index.get("artifacts", []):
        if isinstance(artifact, Mapping) and artifact.get("artifact_name") == artifact_name:
            return artifact
    return None


def _artifact_path_matches_expected(
    artifact_entry: Mapping[str, Any], expected_filename: str
) -> bool:
    artifact_path = artifact_entry.get("artifact_path")
    if not isinstance(artifact_path, str) or not artifact_path.strip():
        return False
    if artifact_path.startswith("/") or artifact_path.startswith("\\"):
        return False
    if re.match(r"^[A-Za-z]:", artifact_path):
        return False
    if "\\" in artifact_path:
        return False

    path_parts = PurePosixPath(artifact_path).parts
    if ".." in path_parts:
        return False

    return PurePosixPath(artifact_path).name == expected_filename


def _required_string_field(
    artifact_entry: Mapping[str, Any], field_name: str
) -> str | None:
    value = artifact_entry.get(field_name)
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def verify_node_start(
    effective_policy: Mapping[str, Any] | None,
    execution_bindings: Mapping[str, Any] | None,
    compiled_artifact_index: Mapping[str, Any] | None,
    node_id: str,
) -> dict[str, Any]:
    if effective_policy is None:
        return {
            "ok": False,
            "message": "missing required compiled artifact: EffectivePolicy.json",
        }

    if execution_bindings is None:
        return {
            "ok": False,
            "message": "missing required compiled artifact: ExecutionBindings.json",
        }

    if compiled_artifact_index is None:
        return {
            "ok": False,
            "message": "missing required compiled artifact: CompiledArtifactIndex.json",
        }

    if effective_policy.get("artifact_lifecycle_state") != "compiled":
        return {
            "ok": False,
            "message": "effective policy is not compiled",
        }

    if execution_bindings.get("artifact_lifecycle_state") != "compiled":
        return {
            "ok": False,
            "message": "execution bindings are not compiled",
        }

    if compiled_artifact_index.get("artifact_lifecycle_state") != "compiled":
        return {
            "ok": False,
            "message": "compiled artifact index is not compiled",
        }

    if effective_policy.get("review_required") is True:
        return {
            "ok": False,
            "message": "approval required before node may start",
        }

    if effective_policy.get("node_id") != node_id:
        return {
            "ok": False,
            "message": f"node_id mismatch for EffectivePolicy.json: {node_id}",
        }

    if execution_bindings.get("node_id") != node_id:
        return {
            "ok": False,
            "message": f"node_id mismatch for ExecutionBindings.json: {node_id}",
        }

    workflow_revision_id = effective_policy.get("workflow_revision_id")
    if execution_bindings.get("workflow_revision_id") != workflow_revision_id:
        return {
            "ok": False,
            "message": "workflow revision mismatch between EffectivePolicy.json and ExecutionBindings.json",
        }

    if compiled_artifact_index.get("workflow_revision_id") != workflow_revision_id:
        return {
            "ok": False,
            "message": "workflow revision mismatch between compiled artifacts and CompiledArtifactIndex.json",
        }

    policy_bundle_digest = effective_policy.get("policy_bundle_digest")
    if execution_bindings.get("policy_bundle_digest") != policy_bundle_digest:
        return {
            "ok": False,
            "message": "policy bundle mismatch between EffectivePolicy.json and ExecutionBindings.json",
        }

    if compiled_artifact_index.get("policy_bundle_digest") != policy_bundle_digest:
        return {
            "ok": False,
            "message": "policy bundle mismatch between compiled artifacts and CompiledArtifactIndex.json",
        }

    effective_policy_entry = _artifact_entry_by_name(
        compiled_artifact_index, "EffectivePolicy"
    )
    execution_bindings_entry = _artifact_entry_by_name(
        compiled_artifact_index, "ExecutionBindings"
    )

    missing_artifact_names = []
    if effective_policy_entry is None:
        missing_artifact_names.append("EffectivePolicy")
    if execution_bindings_entry is None:
        missing_artifact_names.append("ExecutionBindings")
    if missing_artifact_names:
        return {
            "ok": False,
            "message": (
                "compiled artifact index missing required artifacts: "
                + ", ".join(missing_artifact_names)
            ),
        }

    if not _artifact_path_matches_expected(
        effective_policy_entry, "EffectivePolicy.json"
    ):
        return {
            "ok": False,
            "message": "effective policy artifact path mismatch",
        }

    if not _artifact_path_matches_expected(
        execution_bindings_entry, "ExecutionBindings.json"
    ):
        return {
            "ok": False,
            "message": "execution bindings artifact path mismatch",
        }

    effective_policy_artifact_revision_id = _required_string_field(
        effective_policy_entry, "artifact_revision_id"
    )
    if effective_policy_artifact_revision_id is None:
        return {
            "ok": False,
            "message": "effective policy artifact revision missing",
        }

    if (
        effective_policy_artifact_revision_id != effective_policy.get("workflow_revision_id")
        or effective_policy_artifact_revision_id
        != compiled_artifact_index.get("workflow_revision_id")
    ):
        return {
            "ok": False,
            "message": "effective policy artifact revision mismatch",
        }

    execution_bindings_artifact_revision_id = _required_string_field(
        execution_bindings_entry, "artifact_revision_id"
    )
    if execution_bindings_artifact_revision_id is None:
        return {
            "ok": False,
            "message": "execution bindings artifact revision missing",
        }

    if (
        execution_bindings_artifact_revision_id
        != execution_bindings.get("workflow_revision_id")
        or execution_bindings_artifact_revision_id
        != compiled_artifact_index.get("workflow_revision_id")
    ):
        return {
            "ok": False,
            "message": "execution bindings artifact revision mismatch",
        }

    effective_policy_content_digest = _required_string_field(
        effective_policy_entry, "content_digest"
    )
    if effective_policy_content_digest is None:
        return {
            "ok": False,
            "message": "effective policy content digest missing",
        }

    if effective_policy_content_digest != canonical_sha256_hex(effective_policy):
        return {
            "ok": False,
            "message": "effective policy content digest mismatch with CompiledArtifactIndex.json",
        }

    execution_bindings_content_digest = _required_string_field(
        execution_bindings_entry, "content_digest"
    )
    if execution_bindings_content_digest is None:
        return {
            "ok": False,
            "message": "execution bindings content digest missing",
        }

    if execution_bindings_content_digest != canonical_sha256_hex(
        execution_bindings
    ):
        return {
            "ok": False,
            "message": "execution bindings content digest mismatch with CompiledArtifactIndex.json",
        }

    return {
        "ok": True,
        "message": "node may start",
    }
