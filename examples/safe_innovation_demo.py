"""Demo/example: the safe innovation demo flow, end to end.

This is an **example script**, intentionally kept out of ``cli/`` because it can
generate a (demo-local) ``ApprovalDecisions.json``. Keeping it here avoids
implying a supported, general auto-approval product path.

It composes existing functions only:

- `cli.workflow_demo_cli.run_workflow_demo` (the blocked safe no-op demo)
- `orchestrator.safe_run.safe_noop_run` (the approved safe no-op run)
- `runtime.run_status_summary.summarize_run_directory` and
  `tui.run_status_summary_view.render_run_status_summary_view`

It performs **no real execution**, calls no tools/connectors, and changes no
compiler/runtime/planner approval semantics. Any approval it writes is
demo-local, applies to the current run's ``request_id`` only, and is **not** a
general auto-approval mechanism. There is no approval carryover and no authority
subsumption. The runtime remains safe no-op only; the compiler remains the sole
authority boundary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from cli.workflow_demo_cli import run_workflow_demo
from compiler.canonical_json import canonical_json_text
from orchestrator.safe_run import safe_noop_run
from planner.workflow_spec_planner import PLANNER_TEMPLATES
from runtime.run_status_summary import summarize_run_directory
from tui.run_status_summary_view import render_run_status_summary_view


DEFAULT_GOAL = "generate innovation ideas from program data"
DEFAULT_NODE_TYPE_REGISTRY = (
    "fixtures/valid/simple-workflow/input/NodeTypeRegistry.json"
)
DEMO_APPROVAL_NOTICE = (
    "Demo-local only. Any approval generated here is created for this local demo "
    "run and applies to the current run's request only; it is not a general "
    "auto-approval mechanism. No approval carryover, no authority subsumption, "
    "no real execution; safe no-op only."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the safe innovation demo (blocked, optionally approved)."
    )
    parser.add_argument("--run-root", default="runs")
    parser.add_argument("--goal", default=DEFAULT_GOAL)
    parser.add_argument("--node-type-registry", default=DEFAULT_NODE_TYPE_REGISTRY)
    parser.add_argument("--planner-template", choices=PLANNER_TEMPLATES)
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument(
        "--demo-approve-current-request", action="store_true"
    )
    return parser


def _dir_nonempty(path: Path) -> bool:
    return path.exists() and any(path.iterdir())


def _run_summary(run_dir: Path) -> dict[str, Any]:
    summary = summarize_run_directory(run_dir)
    return {
        "run_dir": str(run_dir),
        "summary": summary,
        "summary_view": render_run_status_summary_view(summary),
    }


def run_safe_innovation_demo(
    *,
    run_root: str | Path,
    goal: str = DEFAULT_GOAL,
    node_type_registry_path: str | Path = DEFAULT_NODE_TYPE_REGISTRY,
    planner_template: str | None = None,
    allow_overwrite: bool = False,
    demo_approve_current_request: bool = False,
) -> dict[str, Any]:
    run_root_path = Path(run_root)
    blocked_run_dir = run_root_path / "innovation-demo"
    approved_run_dir = run_root_path / "innovation-approved"

    # Preflight: fail closed before mutating any target directory.
    target_dirs = [blocked_run_dir]
    if demo_approve_current_request:
        target_dirs.append(approved_run_dir)
    if not allow_overwrite:
        for target_dir in target_dirs:
            if _dir_nonempty(target_dir):
                raise FileExistsError(
                    "refusing to write into non-empty demo dir without "
                    f"--allow-overwrite: {target_dir}"
                )

    # Step 1: the blocked safe no-op innovation demo.
    demo_result = run_workflow_demo(
        goal=goal,
        node_type_registry_path=node_type_registry_path,
        run_dir=blocked_run_dir,
        planner_template=planner_template,
        allow_overwrite=allow_overwrite,
    )

    output: dict[str, Any] = {
        "demo_approval_notice": DEMO_APPROVAL_NOTICE,
        "goal": goal,
        "planner_template": demo_result["planner_template"],
        "approval_generated": False,
        "blocked_run": _run_summary(blocked_run_dir),
        "request_id": None,
        "approval_decisions_path": None,
        "approved_run": None,
        "inspect_commands": [
            f"python -m cli.run_status_cli --run-dir {blocked_run_dir} --summary"
        ],
    }

    if not demo_approve_current_request:
        output["message"] = (
            "Approval was not generated. Re-run with "
            "--demo-approve-current-request to approve the current request and "
            "produce a completed safe no-op."
        )
        return output

    # Step 2: generate a demo-local approval for the current request only.
    approval_requests = json.loads(
        (blocked_run_dir / "candidate" / "ApprovalRequests.json").read_text(
            encoding="utf-8"
        )
    )
    request = approval_requests["requests"][0]
    request_id = request["request_id"]
    workflow_revision_id = approval_requests["workflow_revision_id"]

    approval_decisions_path = blocked_run_dir / "ApprovalDecisions.json"
    approval_decisions_path.write_text(
        json.dumps(
            {
                "schema_version": "m1",
                "workflow_revision_id": workflow_revision_id,
                "artifact_lifecycle_state": "completed",
                "decisions": [
                    {
                        "request_id": request_id,
                        "decision": "approved",
                        "approved_by": "safe-innovation-demo-local",
                        "approved_at": "2026-06-06T00:00:00Z",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Step 3: the approved safe no-op run over the same candidate.
    safe_noop_run(
        blocked_run_dir / "candidate" / "WorkflowSpec.json",
        blocked_run_dir / "NodeTypeRegistry.json",
        blocked_run_dir / "candidate" / "RequestedAuth.json",
        blocked_run_dir / "candidate" / "ApprovalRequests.json",
        repo_root=blocked_run_dir,
        output_dir=approved_run_dir,
        node_id="retrieve-1",
        approval_decisions_path=approval_decisions_path,
        allow_overwrite=allow_overwrite,
    )

    output["approval_generated"] = True
    output["message"] = (
        "Approval was generated for the current run's request only (demo-local)."
    )
    output["request_id"] = request_id
    output["approval_decisions_path"] = str(approval_decisions_path)
    output["approved_run"] = _run_summary(approved_run_dir)
    output["inspect_commands"].append(
        f"python -m cli.run_status_cli --run-dir {approved_run_dir} --summary"
    )
    return output


def _exit_ok(output: dict[str, Any]) -> bool:
    run = output["approved_run"] if output["approval_generated"] else output["blocked_run"]
    return run["summary"].get("compilation_status") == "compiled"


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = run_safe_innovation_demo(
        run_root=args.run_root,
        goal=args.goal,
        node_type_registry_path=args.node_type_registry,
        planner_template=args.planner_template,
        allow_overwrite=args.allow_overwrite,
        demo_approve_current_request=args.demo_approve_current_request,
    )
    print(canonical_json_text(output))
    return 0 if _exit_ok(output) else 1


if __name__ == "__main__":
    raise SystemExit(main())
