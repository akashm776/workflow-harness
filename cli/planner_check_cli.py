"""Operator CLI: plan a candidate from a goal, then run compiler validation.

This turns a plain-text goal into candidate input JSON (via the deterministic
planner stub) and runs the compiler's validate/compile path against it. It does
not execute anything and writes only the candidate input files. The compiler
remains the sole authority boundary; planner output is non-authoritative until it
is validated and compiled.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile
from typing import Any, Sequence

from compiler.canonical_json import canonical_json_text
from compiler.compile_run import compile_static_artifacts, summarize_compile_result
from planner.workflow_spec_planner import (
    CANDIDATE_ARTIFACT_FILES,
    build_stub_planner_candidate,
    write_planner_candidate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan a candidate from a goal and run a compiler check."
    )
    parser.add_argument("--goal", required=True)
    parser.add_argument("--node-type-registry", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _compile_candidate_bundle(
    bundle_dir: Path,
    node_type_registry_path: str | Path,
    repo_root: str | Path,
) -> dict[str, Any]:
    compile_result = compile_static_artifacts(
        bundle_dir / "WorkflowSpec.json",
        node_type_registry_path,
        bundle_dir / "RequestedAuth.json",
        bundle_dir / "ApprovalRequests.json",
        repo_root=repo_root,
    )
    return summarize_compile_result(compile_result)


def run_planner_check(
    *,
    goal: str,
    node_type_registry_path: str | Path,
    repo_root: str | Path,
    candidate_dir: str | Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Build a candidate and compile-check it.

    The compile path produces no on-disk compiled, audit, or runtime artifacts.
    In normal mode the candidate input files are written to ``candidate_dir``. In
    ``dry_run`` mode they are written only to a temporary directory that is
    removed before returning, ``candidate_dir`` is not created, and the
    temporary path is never exposed: the reported ``candidate_dir`` is the
    requested target only.
    """

    candidate = build_stub_planner_candidate(goal)
    requested_candidate_dir = str(Path(candidate_dir))

    if dry_run:
        # Compile entirely inside a self-contained temporary bundle so nothing is
        # written under the operator's repo root or the requested candidate dir.
        # The registry is copied in so every artifact path resolves under the
        # temp root; the temp path is never surfaced in output.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            write_planner_candidate(candidate, tmp_path)
            shutil.copy(node_type_registry_path, tmp_path / "NodeTypeRegistry.json")
            compile_summary = _compile_candidate_bundle(
                tmp_path, tmp_path / "NodeTypeRegistry.json", repo_root=tmp_path
            )
        written = list(CANDIDATE_ARTIFACT_FILES)
    else:
        write_manifest = write_planner_candidate(candidate, candidate_dir)
        compile_summary = _compile_candidate_bundle(
            Path(candidate_dir), node_type_registry_path, repo_root=repo_root
        )
        written = write_manifest["written"]

    return {
        "candidate": candidate,
        "compile_summary": compile_summary,
        "dry_run": dry_run,
        "candidate_dir": requested_candidate_dir,
        "written": written,
    }


def build_default_output(check_result: dict[str, Any]) -> dict[str, Any]:
    candidate = check_result["candidate"]
    output: dict[str, Any] = {
        "planner_result": {
            "planner_version": candidate["planner_version"],
            "candidate_dir": check_result["candidate_dir"],
            "written": check_result["written"],
        },
        "compile_summary": check_result["compile_summary"],
    }
    if check_result["dry_run"]:
        output["dry_run"] = True
    return output


def build_summary_only_output(check_result: dict[str, Any]) -> dict[str, Any]:
    compile_summary = check_result["compile_summary"]
    output: dict[str, Any] = {
        "ok": compile_summary["ok"],
        "compilation_status": compile_summary["compilation_status"],
        "diagnostics": compile_summary["diagnostics"],
        "candidate_dir": check_result["candidate_dir"],
    }
    if check_result["dry_run"]:
        output["dry_run"] = True
    return output


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    check_result = run_planner_check(
        goal=args.goal,
        node_type_registry_path=args.node_type_registry,
        repo_root=args.repo_root,
        candidate_dir=args.candidate_dir,
        dry_run=args.dry_run,
    )

    if args.summary_only:
        printed_result = build_summary_only_output(check_result)
    else:
        printed_result = build_default_output(check_result)

    print(canonical_json_text(printed_result))
    return 0 if check_result["compile_summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
