from __future__ import annotations

from pathlib import Path
from typing import Any

from audit.audit_log_writer import append_audit_events
from orchestrator.compile_and_verify import (
    build_orchestration_audit_events,
    compile_write_load_verify,
    execute_noop_for_orchestration_result,
    write_execution_manifest_for_orchestration_result,
)
from runtime.execution_result_writer import write_execution_result


def safe_noop_run(
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
    orchestration_result = compile_write_load_verify(
        workflow_spec_path,
        node_type_registry_path,
        requested_auth_path,
        approval_requests_path,
        repo_root=repo_root,
        output_dir=output_dir,
        node_id=node_id,
        approval_decisions_path=approval_decisions_path,
        allow_overwrite=allow_overwrite,
    )
    audit_events = build_orchestration_audit_events(orchestration_result)
    audit_log_result = append_audit_events(
        Path(output_dir) / "AuditLog.jsonl",
        audit_events,
    )
    execution_manifest_write_result = write_execution_manifest_for_orchestration_result(
        orchestration_result,
        output_dir,
        allow_overwrite=allow_overwrite,
    )
    noop_execution = execute_noop_for_orchestration_result(orchestration_result)

    execution_result_write_result: dict[str, Any] | None = None
    if noop_execution is not None:
        execution_result_write_result = write_execution_result(
            noop_execution["execution_result"],
            output_dir,
            allow_overwrite=allow_overwrite,
        )

    return {
        "orchestration_result": orchestration_result,
        "audit_log_result": audit_log_result,
        "execution_manifest_write_result": execution_manifest_write_result,
        "noop_execution": noop_execution,
        "execution_result_write_result": execution_result_write_result,
    }
