"""End-to-end safe no-op workflow demo CLI.

Composes existing pieces into one operator loop: build a deterministic planner
candidate from a goal, write it into a self-contained run directory, and run the
existing safe no-op path (compile -> write -> load -> verify -> no-op) over it.

This adds **no** real execution. It calls no tools or connectors, implements no
sandbox/broker, and makes no planner output authoritative. The compiler remains
the sole authority boundary and the runtime remains safe no-op only.

The demo is self-contained: the candidate inputs and a copy of the provided
`NodeTypeRegistry.json` are written under `--run-dir`, and compilation/run use
`repo_root = --run-dir`. `--repo-root` is accepted for interface symmetry but is
not used as the effective compile root here; the effective root is reported as
`effective_repo_root` in the summary.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
from typing import Any, Sequence

from compiler.canonical_json import canonical_json_text
from orchestrator.safe_run import safe_noop_run
from planner.workflow_spec_planner import (
    select_planner_candidate,
    write_planner_candidate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an end-to-end safe no-op workflow demo from a goal."
    )
    parser.add_argument("--goal", required=True)
    parser.add_argument("--node-type-registry", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--node-id", default="retrieve-1")
    parser.add_argument("--allow-overwrite", action="store_true")
    return parser


def run_workflow_demo(
    *,
    goal: str,
    node_type_registry_path: str | Path,
    run_dir: str | Path,
    node_id: str = "retrieve-1",
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    """Build a candidate, materialize a self-contained bundle, run the safe path.

    Writes only the existing safe artifacts. The effective compile root is the
    run directory; the original repo root is not used as an authority source.
    """

    run_path = Path(run_dir)
    candidate_dir = run_path / "candidate"

    # Preflight: fail closed before writing anything into a non-empty run dir, so
    # a rerun without --allow-overwrite never partially mutates it.
    if not allow_overwrite and run_path.exists() and any(run_path.iterdir()):
        raise FileExistsError(
            f"refusing to write into non-empty run dir without --allow-overwrite: "
            f"{run_path}"
        )

    run_path.mkdir(parents=True, exist_ok=True)

    planner_template, candidate = select_planner_candidate(goal)
    write_planner_candidate(candidate, candidate_dir)

    registry_dest = run_path / "NodeTypeRegistry.json"
    shutil.copy(node_type_registry_path, registry_dest)

    run_result = safe_noop_run(
        candidate_dir / "WorkflowSpec.json",
        registry_dest,
        candidate_dir / "RequestedAuth.json",
        candidate_dir / "ApprovalRequests.json",
        repo_root=run_path,
        output_dir=run_path,
        node_id=node_id,
        allow_overwrite=allow_overwrite,
    )

    return {
        "goal": goal,
        "planner_template": planner_template,
        "candidate_dir": str(candidate_dir),
        "run_dir": str(run_path),
        "effective_repo_root": str(run_path),
        "run_result": run_result,
    }


def build_demo_summary(demo_result: dict[str, Any]) -> dict[str, Any]:
    run_result = demo_result["run_result"]
    orchestration_result = run_result["orchestration_result"]
    compile_summary = orchestration_result["compile_summary"]

    execution_status = None
    noop_execution = run_result.get("noop_execution")
    if isinstance(noop_execution, dict):
        execution_result = noop_execution.get("execution_result")
        if isinstance(execution_result, dict):
            execution_status = execution_result.get("execution_status")

    run_dir = demo_result["run_dir"]
    return {
        "ok": bool(compile_summary["ok"]),
        "goal": demo_result["goal"],
        "planner_template": demo_result["planner_template"],
        "candidate_dir": demo_result["candidate_dir"],
        "run_dir": run_dir,
        "effective_repo_root": demo_result["effective_repo_root"],
        "compilation_status": compile_summary["compilation_status"],
        "execution_status": execution_status,
        "status_command": (
            f"python -m cli.run_status_cli --run-dir {run_dir} --view"
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    demo_result = run_workflow_demo(
        goal=args.goal,
        node_type_registry_path=args.node_type_registry,
        run_dir=args.run_dir,
        node_id=args.node_id,
        allow_overwrite=args.allow_overwrite,
    )
    summary = build_demo_summary(demo_result)
    print(canonical_json_text(summary))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
