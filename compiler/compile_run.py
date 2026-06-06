from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from compiler.approval_resolution import ConflictingApprovalDecisionsError
from compiler.authority_value_validator import (
    DisallowedAuthorityValueError,
    assert_no_disallowed_authority_values,
)
from compiler.compilation_report import build_compilation_report
from compiler.compiled_artifact_index import build_compiled_artifact_index
from compiler.effective_policy import build_effective_policy
from compiler.execution_bindings import build_execution_bindings


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _resolve_approval_decisions_path(
    approval_decisions_path: str | Path | None,
    approval_requests_path: str | Path,
) -> str | Path | None:
    if approval_decisions_path is not None:
        return approval_decisions_path
    candidate = Path(approval_requests_path).with_name("ApprovalDecisions.json")
    if candidate.exists():
        return candidate
    return None


def _build_conflicting_approval_report(workflow_spec_path: str | Path) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)
    return {
        "schema_version": "m1",
        "graph_revision_id": workflow_spec["graph_revision_id"],
        "workflow_revision_id": workflow_spec["workflow_revision_id"],
        "policy_bundle_digest": workflow_spec["policy_bundle_digest"],
        "artifact_lifecycle_state": "failed",
        "status": "failed",
        "diagnostics": [
            {
                "error_code": "CONFLICTING_APPROVAL_DECISIONS",
                "component": "approval_validator",
                "artifact": "ApprovalDecisions.json",
                "message": "conflicting approval decisions for the same node_id and approval_subject_hash",
            }
        ],
    }


def _build_disallowed_authority_report(
    workflow_spec_path: str | Path, error: DisallowedAuthorityValueError
) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)
    detail = "; ".join(
        f"{finding['path']} ({finding['reason']})" for finding in error.findings
    )
    report: dict[str, Any] = {"schema_version": "m1"}
    # Only copy identity fields when they are strings, so a failed report built
    # because of a disallowed value never re-emits that disallowed value.
    for field_name in (
        "graph_revision_id",
        "workflow_revision_id",
        "policy_bundle_digest",
    ):
        value = workflow_spec.get(field_name)
        if isinstance(value, str):
            report[field_name] = value
    report.update(
        {
            "artifact_lifecycle_state": "failed",
            "status": "failed",
            "diagnostics": [
                {
                    "error_code": "DISALLOWED_AUTHORITY_VALUE",
                    "component": "authority_value_validator",
                    "artifact": error.artifact_name,
                    "message": (
                        f"disallowed authority value in {error.artifact_name}: {detail}"
                    ),
                }
            ],
        }
    )
    return report


def compile_static_artifacts(
    workflow_spec_path: str | Path,
    node_type_registry_path: str | Path,
    requested_auth_path: str | Path,
    approval_requests_path: str | Path,
    *,
    repo_root: str | Path,
    approval_decisions_path: str | Path | None = None,
) -> dict[str, Any]:
    resolved_approval_decisions_path = _resolve_approval_decisions_path(
        approval_decisions_path, approval_requests_path
    )

    compilation_report = build_compilation_report(
        workflow_spec_path,
        node_type_registry_path,
        requested_auth_path,
        approval_requests_path,
        approval_decisions_path=resolved_approval_decisions_path,
    )

    compilation_report_output_path = Path(workflow_spec_path).with_name(
        "CompilationReport.json"
    )
    artifacts: dict[str, Any] = {
        "CompilationReport.json": compilation_report,
    }

    effective_policy: dict[str, Any] | None = None
    effective_policy_output_path: Path | None = None
    execution_bindings: dict[str, Any] | None = None
    execution_bindings_output_path: Path | None = None

    if compilation_report.get("status") == "compiled":
        try:
            effective_policy = build_effective_policy(
                workflow_spec_path,
                requested_auth_path,
                node_type_registry_path,
                resolved_approval_decisions_path,
                approval_requests_path,
            )
            effective_policy_output_path = Path(workflow_spec_path).with_name(
                "EffectivePolicy.json"
            )
            artifacts["EffectivePolicy.json"] = effective_policy

            execution_bindings = build_execution_bindings(effective_policy)
            execution_bindings_output_path = Path(workflow_spec_path).with_name(
                "ExecutionBindings.json"
            )
            artifacts["ExecutionBindings.json"] = execution_bindings

            # Defensive gate: emitted authority artifacts are derived from
            # already-validated inputs, so this should never fire in valid flows.
            # It guards against a regression introducing a float/non-finite value
            # into authority artifacts before they are hashed into the index.
            assert_no_disallowed_authority_values(
                effective_policy, artifact_name="EffectivePolicy.json"
            )
            assert_no_disallowed_authority_values(
                execution_bindings, artifact_name="ExecutionBindings.json"
            )
            assert_no_disallowed_authority_values(
                compilation_report, artifact_name="CompilationReport.json"
            )
        except ConflictingApprovalDecisionsError:
            compilation_report = _build_conflicting_approval_report(workflow_spec_path)
            artifacts = {
                "CompilationReport.json": compilation_report,
            }
            effective_policy = None
            effective_policy_output_path = None
            execution_bindings = None
            execution_bindings_output_path = None
        except DisallowedAuthorityValueError as error:
            compilation_report = _build_disallowed_authority_report(
                workflow_spec_path, error
            )
            artifacts = {
                "CompilationReport.json": compilation_report,
            }
            effective_policy = None
            effective_policy_output_path = None
            execution_bindings = None
            execution_bindings_output_path = None

    compiled_artifact_index = build_compiled_artifact_index(
        workflow_spec_path,
        node_type_registry_path,
        requested_auth_path,
        approval_requests_path,
        compilation_report,
        compilation_report_output_path,
        effective_policy,
        effective_policy_output_path,
        execution_bindings,
        execution_bindings_output_path,
        repo_root=repo_root,
    )

    # Validate the index after it is built. If a disallowed value slipped in,
    # fail closed: rebuild a failed report and a clean failed index.
    try:
        assert_no_disallowed_authority_values(
            compiled_artifact_index, artifact_name="CompiledArtifactIndex.json"
        )
    except DisallowedAuthorityValueError as error:
        compilation_report = _build_disallowed_authority_report(
            workflow_spec_path, error
        )
        artifacts = {
            "CompilationReport.json": compilation_report,
        }
        compiled_artifact_index = build_compiled_artifact_index(
            workflow_spec_path,
            node_type_registry_path,
            requested_auth_path,
            approval_requests_path,
            compilation_report,
            compilation_report_output_path,
            None,
            None,
            None,
            None,
            repo_root=repo_root,
        )

    artifacts["CompiledArtifactIndex.json"] = compiled_artifact_index

    return {
        "ok": compilation_report.get("status") == "compiled",
        "artifacts": artifacts,
    }


def summarize_compile_result(compile_result: dict[str, Any]) -> dict[str, Any]:
    artifacts = compile_result.get("artifacts", {})
    effective_policy = artifacts.get("EffectivePolicy.json", {})
    compilation_report = artifacts.get("CompilationReport.json", {})

    return {
        "ok": bool(compile_result.get("ok")),
        "emitted_artifacts": sorted(artifacts.keys()),
        "compilation_status": compilation_report.get("status"),
        "diagnostics": compilation_report.get("diagnostics", []),
        "may_runtime_start_possible": (
            "EffectivePolicy.json" in artifacts
            and "ExecutionBindings.json" in artifacts
            and effective_policy.get("review_required") is False
        ),
    }
