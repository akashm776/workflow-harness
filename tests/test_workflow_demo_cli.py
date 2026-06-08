from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from cli import workflow_demo_cli
from runtime.run_status import inspect_run_directory


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_NODE_TYPE_REGISTRY = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "NodeTypeRegistry.json"
)
CANDIDATE_FILES = ("ApprovalRequests.json", "RequestedAuth.json", "WorkflowSpec.json")
SAFE_ARTIFACTS = (
    "CompilationReport.json",
    "CompiledArtifactIndex.json",
    "EffectivePolicy.json",
    "ExecutionBindings.json",
    "ExecutionManifest.json",
    "ExecutionResult.json",
    "AuditLog.jsonl",
)


class WorkflowDemoCliTests(unittest.TestCase):
    def _run(
        self,
        goal: str,
        run_dir: Path,
        *,
        planner_template: str | None = None,
        allow_overwrite: bool = False,
    ):
        argv = [
            "--goal", goal,
            "--node-type-registry", str(SIMPLE_NODE_TYPE_REGISTRY),
            "--repo-root", ".",
            "--run-dir", str(run_dir),
        ]
        if planner_template is not None:
            argv.extend(["--planner-template", planner_template])
        if allow_overwrite:
            argv.append("--allow-overwrite")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return_code = workflow_demo_cli.main(argv)
        return return_code, json.loads(stdout.getvalue())

    def test_end_to_end_demo_produces_safe_noop_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            return_code, summary = self._run(
                "generate innovation ideas from program data", run_dir
            )

            # Exit 0 and summary shape.
            self.assertEqual(return_code, 0)
            self.assertTrue(summary["ok"])
            self.assertEqual(
                summary["goal"], "generate innovation ideas from program data"
            )
            self.assertEqual(summary["candidate_dir"], str(run_dir / "candidate"))
            self.assertEqual(summary["run_dir"], str(run_dir))
            self.assertEqual(summary["effective_repo_root"], str(run_dir))
            self.assertEqual(summary["compilation_status"], "compiled")
            self.assertIn(
                f"python -m cli.run_status_cli --run-dir {run_dir} --view",
                summary["status_command"],
            )

            # Candidate inputs written under <run-dir>/candidate.
            candidate_names = sorted(
                p.name for p in (run_dir / "candidate").iterdir()
            )
            self.assertEqual(candidate_names, list(CANDIDATE_FILES))

            # Registry copied into run dir; safe artifacts present.
            self.assertTrue((run_dir / "NodeTypeRegistry.json").exists())
            for artifact in SAFE_ARTIFACTS:
                self.assertTrue((run_dir / artifact).exists(), artifact)

            # Run dir is a complete safe no-op run.
            self.assertTrue(
                inspect_run_directory(run_dir)["complete_safe_noop_run"]
            )

    def test_execution_is_safe_noop_not_real_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            _, summary = self._run("safe noop goal", run_dir)

            # A safe no-op status only (no real execution). The candidate
            # requests authority and ships no approval decision, so review is
            # required and the no-op is "blocked"; "completed" is the other safe
            # no-op outcome. Neither performs real work.
            self.assertIn(summary["execution_status"], ("completed", "blocked"))
            execution_result = json.loads(
                (run_dir / "ExecutionResult.json").read_text(encoding="utf-8")
            )
            self.assertEqual(execution_result["side_effects"], [])
            self.assertEqual(execution_result["produced_evidence"], [])

    def test_goal_not_written_into_candidate_authority_artifacts(self) -> None:
        goal = "SENTINEL-DEMO-GOAL-DO-NOT-LEAK"
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            self._run(goal, run_dir)
            for file_name in CANDIDATE_FILES:
                content = (run_dir / "candidate" / file_name).read_text(
                    encoding="utf-8"
                )
                self.assertNotIn(goal, content)

    def test_deterministic_candidate_for_same_goal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_a = Path(tmp) / "a"
            run_b = Path(tmp) / "b"
            self._run("same goal", run_a)
            self._run("same goal", run_b)

            spec_a = (run_a / "candidate" / "WorkflowSpec.json").read_text(
                encoding="utf-8"
            )
            spec_b = (run_b / "candidate" / "WorkflowSpec.json").read_text(
                encoding="utf-8"
            )
            self.assertEqual(spec_a, spec_b)

    def test_rerun_without_allow_overwrite_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            self._run("first run", run_dir)

            # Capture pre-rerun contents.
            workflow_spec_path = run_dir / "candidate" / "WorkflowSpec.json"
            registry_path = run_dir / "NodeTypeRegistry.json"
            workflow_spec_before = workflow_spec_path.read_text(encoding="utf-8")
            registry_before = registry_path.read_text(encoding="utf-8")

            with self.assertRaises(FileExistsError):
                self._run("second run", run_dir)

            # The failed rerun must not have mutated existing files.
            self.assertEqual(
                workflow_spec_path.read_text(encoding="utf-8"), workflow_spec_before
            )
            self.assertEqual(
                registry_path.read_text(encoding="utf-8"), registry_before
            )

    def test_rerun_with_allow_overwrite_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            self._run("first run", run_dir)
            return_code, summary = self._run(
                "second run", run_dir, allow_overwrite=True
            )
            self.assertEqual(return_code, 0)
            self.assertTrue(summary["ok"])

    def test_innovation_goal_summary_reports_innovation_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            _, summary = self._run(
                "generate innovation ideas from program data", run_dir
            )
            self.assertEqual(summary["planner_template"], "innovation")

    def test_unrelated_goal_summary_reports_stub_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            _, summary = self._run("summarize the quarterly report", run_dir)
            self.assertEqual(summary["planner_template"], "stub")

    def test_explicit_innovation_review_template_reports_selected_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            _, summary = self._run(
                "summarize the quarterly report",
                run_dir,
                planner_template="innovation_review",
            )
            self.assertEqual(summary["planner_template"], "innovation_review")
            self.assertEqual(summary["compilation_status"], "compiled")
            self.assertEqual(summary["execution_status"], "blocked")

    def test_explicit_template_does_not_change_default_innovation_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            _, summary = self._run(
                "generate innovation ideas from program data",
                run_dir,
            )
            self.assertEqual(summary["planner_template"], "innovation")


if __name__ == "__main__":
    unittest.main()
