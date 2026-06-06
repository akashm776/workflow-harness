from __future__ import annotations

import argparse
from typing import Any
from typing import Sequence

from compiler.canonical_json import canonical_json_text
from compiler.compile_run import compile_static_artifacts, summarize_compile_result
from orchestrator.safe_run import safe_noop_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the safe no-op workflow path.")
    parser.add_argument("--workflow-spec", required=True)
    parser.add_argument("--node-type-registry", required=True)
    parser.add_argument("--requested-auth", required=True)
    parser.add_argument("--approval-requests", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--approval-decisions")
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    return parser


def build_operator_summary(result: dict[str, Any]) -> dict[str, Any]:
    orchestration_result = result["orchestration_result"]
    compile_summary = orchestration_result["compile_summary"]
    write_manifest = orchestration_result["write_manifest"]

    summary: dict[str, Any] = {
        "ok": compile_summary["ok"],
        "compilation_status": compile_summary["compilation_status"],
        "emitted_artifacts": compile_summary["emitted_artifacts"],
        "may_runtime_start_possible": compile_summary["may_runtime_start_possible"],
        "output_dir": write_manifest["output_dir"],
    }

    audit_log_result = result.get("audit_log_result")
    if (
        isinstance(audit_log_result, dict)
        and audit_log_result.get("ok") is True
        and "audit_log_path" in audit_log_result
    ):
        summary["audit_log_path"] = audit_log_result["audit_log_path"]

    noop_execution = result.get("noop_execution")
    if isinstance(noop_execution, dict):
        execution_result = noop_execution.get("execution_result")
        if isinstance(execution_result, dict) and "execution_status" in execution_result:
            summary["execution_status"] = execution_result["execution_status"]

    return summary


def build_dry_run_result(
    compile_result: dict[str, Any],
    compile_summary: dict[str, Any],
    *,
    output_dir: str,
) -> dict[str, Any]:
    return {
        "compile_result": compile_result,
        "compile_summary": compile_summary,
        "dry_run": True,
        "output_dir": output_dir,
    }


def build_dry_run_operator_summary(
    compile_summary: dict[str, Any],
    *,
    output_dir: str,
) -> dict[str, Any]:
    return {
        "ok": compile_summary["ok"],
        "compilation_status": compile_summary["compilation_status"],
        "emitted_artifacts": compile_summary["emitted_artifacts"],
        "may_runtime_start_possible": compile_summary["may_runtime_start_possible"],
        "output_dir": output_dir,
    }


def build_check_result(compile_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": compile_summary["ok"],
        "compilation_status": compile_summary["compilation_status"],
        "diagnostics": compile_summary["diagnostics"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.check or args.dry_run:
        compile_result = compile_static_artifacts(
            args.workflow_spec,
            args.node_type_registry,
            args.requested_auth,
            args.approval_requests,
            repo_root=args.repo_root,
            approval_decisions_path=args.approval_decisions,
        )
        compile_summary = summarize_compile_result(compile_result)
        if args.check:
            printed_result = build_check_result(compile_summary)
        else:
            printed_result = (
                build_dry_run_operator_summary(
                    compile_summary,
                    output_dir=args.output_dir,
                )
                if args.summary_only
                else build_dry_run_result(
                    compile_result,
                    compile_summary,
                    output_dir=args.output_dir,
                )
            )
        print(canonical_json_text(printed_result))
        return 0 if compile_summary["ok"] else 1

    result = safe_noop_run(
        args.workflow_spec,
        args.node_type_registry,
        args.requested_auth,
        args.approval_requests,
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        node_id=args.node_id,
        approval_decisions_path=args.approval_decisions,
        allow_overwrite=args.allow_overwrite,
    )
    printed_result = build_operator_summary(result) if args.summary_only else result
    print(canonical_json_text(printed_result))
    return 0 if result["orchestration_result"]["compile_summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
