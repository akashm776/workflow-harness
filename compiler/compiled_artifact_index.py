from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from compiler.canonical_json import canonical_sha256_hex
from compiler.dependency_digest import (
    CANONICALIZATION_VERSION,
    HASH_ALGORITHM,
    make_dependency_digest_entry,
    normalize_dependency_digest_entries,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _relative_artifact_path(path: str | Path, root: str | Path) -> str:
    absolute_path = Path(path).resolve()
    absolute_root = Path(root).resolve()
    return absolute_path.relative_to(absolute_root).as_posix()


def build_compiled_artifact_index(
    workflow_spec_path: str | Path,
    node_type_registry_path: str | Path,
    requested_auth_path: str | Path,
    approval_requests_path: str | Path,
    compilation_report: dict[str, Any],
    compilation_report_output_path: str | Path,
    effective_policy: dict[str, Any] | None = None,
    effective_policy_output_path: str | Path | None = None,
    execution_bindings: dict[str, Any] | None = None,
    execution_bindings_output_path: str | Path | None = None,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve() if repo_root is not None else Path.cwd().resolve()

    workflow_spec = _load_json(workflow_spec_path)
    node_type_registry = _load_json(node_type_registry_path)
    requested_auth = _load_json(requested_auth_path)
    approval_requests = _load_json(approval_requests_path)

    # Only treat identity/revision values as usable when they are strings. A
    # non-string (e.g. a float or non-finite value that failed validation) is
    # omitted so a failed index never re-emits a disallowed authority value.
    raw_workflow_revision_id = workflow_spec.get("workflow_revision_id")
    workflow_revision_id = (
        raw_workflow_revision_id
        if isinstance(raw_workflow_revision_id, str)
        else None
    )

    dependency_entries = normalize_dependency_digest_entries(
        [
            make_dependency_digest_entry(
                artifact_group="proposal",
                artifact_path=_relative_artifact_path(workflow_spec_path, root),
                content_digest=canonical_sha256_hex(workflow_spec),
                revision_id=workflow_revision_id,
            ),
            make_dependency_digest_entry(
                artifact_group="static_governance",
                artifact_path=_relative_artifact_path(node_type_registry_path, root),
                content_digest=canonical_sha256_hex(node_type_registry),
            ),
            make_dependency_digest_entry(
                artifact_group="proposal",
                artifact_path=_relative_artifact_path(requested_auth_path, root),
                content_digest=canonical_sha256_hex(requested_auth),
                revision_id=workflow_revision_id,
            ),
            make_dependency_digest_entry(
                artifact_group="run_scoped_governance",
                artifact_path=_relative_artifact_path(approval_requests_path, root),
                content_digest=canonical_sha256_hex(approval_requests),
                revision_id=workflow_revision_id,
            ),
        ]
    )

    def _artifact_entry(
        artifact_name: str, artifact_output_path: str | Path, artifact: dict[str, Any]
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "artifact_name": artifact_name,
            "artifact_path": _relative_artifact_path(artifact_output_path, root),
            "content_digest": canonical_sha256_hex(artifact),
        }
        if workflow_revision_id is not None:
            entry["artifact_revision_id"] = workflow_revision_id
        return entry

    artifact_entries = [
        _artifact_entry(
            "CompilationReport", compilation_report_output_path, compilation_report
        )
    ]

    if effective_policy is not None and effective_policy_output_path is not None:
        artifact_entries.append(
            _artifact_entry(
                "EffectivePolicy", effective_policy_output_path, effective_policy
            )
        )

    if execution_bindings is not None and execution_bindings_output_path is not None:
        artifact_entries.append(
            _artifact_entry(
                "ExecutionBindings", execution_bindings_output_path, execution_bindings
            )
        )

    index: dict[str, Any] = {"schema_version": "m1"}
    for field_name in (
        "graph_revision_id",
        "workflow_revision_id",
        "policy_bundle_digest",
    ):
        value = workflow_spec.get(field_name)
        if isinstance(value, str):
            index[field_name] = value
    index.update(
        {
            "artifact_lifecycle_state": (
                "compiled"
                if compilation_report.get("status") == "compiled"
                else "failed"
            ),
            "compiler_version": "m1-local",
            "hash_algorithm": HASH_ALGORITHM,
            "canonicalization_version": CANONICALIZATION_VERSION,
            "declared_input_dependency_digests": dependency_entries,
            "artifacts": artifact_entries,
        }
    )
    return index
