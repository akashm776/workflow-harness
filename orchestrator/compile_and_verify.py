from __future__ import annotations

from pathlib import Path
from typing import Any

from audit.audit_event import make_audit_event
from compiler.canonical_json import canonical_json_text
from compiler.artifact_writer import write_compiled_artifacts
from compiler.compile_run import compile_static_artifacts, summarize_compile_result
from runtime.artifact_loader import load_runtime_bundle
from runtime.execution_manifest import build_execution_manifest
from runtime.noop_executor import execute_noop_node
from runtime.runtime_verifier import verify_node_start


def compile_write_load_verify(
    workflow_spec_path: str | Path,
    node_type_registry_path: str | Path,
    requested_auth_path: str | Path,
    approval_requests_path: str | Path,
    *,
    repo_root: str | Path,
    output_dir: str | Path,
    node_id: str,
    approval_decisions_path: str | Path | None = None,
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    compile_result = compile_static_artifacts(
        workflow_spec_path,
        node_type_registry_path,
        requested_auth_path,
        approval_requests_path,
        repo_root=repo_root,
        approval_decisions_path=approval_decisions_path,
    )
    workflow_revision_id = compile_result["artifacts"]["CompilationReport.json"].get(
        "workflow_revision_id"
    )
    compile_summary = summarize_compile_result(compile_result)
    write_manifest = write_compiled_artifacts(
        compile_result,
        output_dir,
        allow_overwrite=allow_overwrite,
    )

    if not compile_summary["may_runtime_start_possible"]:
        return {
            "workflow_revision_id": workflow_revision_id,
            "node_id": node_id,
            "compile_summary": compile_summary,
            "write_manifest": write_manifest,
            "load_result_ok": False,
            "verifier_result": None,
        }

    load_result = load_runtime_bundle(output_dir)
    if not load_result["ok"]:
        return {
            "workflow_revision_id": workflow_revision_id,
            "node_id": node_id,
            "compile_summary": compile_summary,
            "write_manifest": write_manifest,
            "load_result_ok": False,
            "verifier_result": None,
        }

    verifier_result = verify_node_start(
        load_result["effective_policy"],
        load_result["execution_bindings"],
        load_result["compiled_artifact_index"],
        node_id,
    )
    return {
        "workflow_revision_id": workflow_revision_id,
        "node_id": node_id,
        "compile_summary": compile_summary,
        "write_manifest": write_manifest,
        "load_result_ok": True,
        "verifier_result": verifier_result,
    }


def build_orchestration_audit_events(
    orchestration_result: dict[str, Any],
) -> list[dict[str, Any]]:
    compile_summary = orchestration_result["compile_summary"]
    write_manifest = orchestration_result["write_manifest"]
    verifier_result = orchestration_result.get("verifier_result")
    workflow_revision_id = orchestration_result["workflow_revision_id"]
    node_id = orchestration_result["node_id"]

    compile_event_type = (
        "compile_completed" if compile_summary["ok"] else "compile_failed"
    )
    compile_status = (
        compile_summary["compilation_status"] if compile_summary["ok"] else "failed"
    )

    events = [
        make_audit_event(
            event_type=compile_event_type,
            actor="orchestrator",
            workflow_revision_id=workflow_revision_id,
            node_id=node_id,
            status=compile_status,
            details={
                "emitted_artifacts": compile_summary["emitted_artifacts"],
                "diagnostics": compile_summary["diagnostics"],
                "may_runtime_start_possible": compile_summary[
                    "may_runtime_start_possible"
                ],
            },
        ),
        make_audit_event(
            event_type="artifacts_written",
            actor="orchestrator",
            workflow_revision_id=workflow_revision_id,
            node_id=node_id,
            status="completed",
            details={
                "output_dir": write_manifest["output_dir"],
                "written_artifacts": write_manifest["written_artifacts"],
            },
        ),
    ]

    if verifier_result is None:
        events.append(
            make_audit_event(
                event_type="runtime_verification_skipped",
                actor="orchestrator",
                workflow_revision_id=workflow_revision_id,
                node_id=node_id,
                status="skipped",
                details={
                    "load_result_ok": orchestration_result["load_result_ok"],
                    "may_runtime_start_possible": compile_summary[
                        "may_runtime_start_possible"
                    ],
                },
            )
        )
    else:
        events.append(
            make_audit_event(
                event_type="runtime_verification_completed",
                actor="orchestrator",
                workflow_revision_id=workflow_revision_id,
                node_id=node_id,
                status="completed" if verifier_result.get("ok") else "failed",
                details={"verifier_result": verifier_result},
            )
        )

    return events


def build_execution_manifest_for_orchestration_result(
    orchestration_result: dict[str, Any],
) -> dict[str, Any] | None:
    compile_summary = orchestration_result["compile_summary"]
    if not compile_summary["ok"]:
        return None

    verifier_result = orchestration_result.get("verifier_result")
    execution_status = (
        "ready_to_execute"
        if verifier_result is not None and verifier_result.get("ok") is True
        else "blocked"
    )
    return build_execution_manifest(
        node_id=orchestration_result["node_id"],
        workflow_revision_id=orchestration_result["workflow_revision_id"],
        verifier_result=verifier_result,
        execution_status=execution_status,
    )


def write_execution_manifest_for_orchestration_result(
    orchestration_result: dict[str, Any],
    output_dir: str | Path,
    *,
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    execution_manifest = build_execution_manifest_for_orchestration_result(
        orchestration_result
    )
    if execution_manifest is None:
        return {
            "ok": True,
            "execution_manifest_written": False,
            "execution_manifest_path": None,
            "execution_manifest": None,
        }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    manifest_path = output_path / "ExecutionManifest.json"
    if manifest_path.exists() and not allow_overwrite:
        raise FileExistsError(
            "refusing to overwrite existing artifact: ExecutionManifest.json"
        )

    manifest_path.write_text(
        canonical_json_text(execution_manifest),
        encoding="utf-8",
    )
    return {
        "ok": True,
        "execution_manifest_written": True,
        "execution_manifest_path": str(manifest_path),
        "execution_manifest": execution_manifest,
    }


def execute_noop_for_orchestration_result(
    orchestration_result: dict[str, Any],
) -> dict[str, Any] | None:
    execution_manifest = build_execution_manifest_for_orchestration_result(
        orchestration_result
    )
    if execution_manifest is None:
        return None

    return {
        "execution_manifest": execution_manifest,
        "execution_result": execute_noop_node(execution_manifest),
    }
