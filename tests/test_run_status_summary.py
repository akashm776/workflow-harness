from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from cli.workflow_demo_cli import run_workflow_demo
from orchestrator.safe_run import safe_noop_run
from runtime.run_status_summary import summarize_run_directory


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
SIMPLE_NODE_TYPE_REGISTRY = SIMPLE_WORKFLOW / "NodeTypeRegistry.json"


class SummarizeRunDirectoryTests(unittest.TestCase):
    def _completed_run(self, output_dir: Path) -> None:
        safe_noop_run(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

    def test_completed_run_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            self._completed_run(run_dir)

            summary = summarize_run_directory(run_dir)

            self.assertEqual(summary["run_dir"], str(run_dir))
            self.assertTrue(summary["complete_safe_noop_run"])
            self.assertEqual(summary["compilation_status"], "compiled")
            self.assertEqual(summary["execution_status"], "completed")
            self.assertIs(summary["review_required"], False)
            self.assertFalse(summary["blocked_by_review"])
            self.assertFalse(summary["candidate_dir_present"])
            self.assertIn("artifacts", summary)
            self.assertIn(
                f"python -m cli.run_status_cli --run-dir {run_dir} --view",
                summary["status_command"],
            )

    def test_blocked_demo_run_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="blocked demo",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            summary = summarize_run_directory(run_dir)

            self.assertTrue(summary["complete_safe_noop_run"])
            self.assertEqual(summary["compilation_status"], "compiled")
            self.assertEqual(summary["execution_status"], "blocked")
            self.assertIs(summary["review_required"], True)
            self.assertTrue(summary["blocked_by_review"])
            self.assertTrue(summary["candidate_dir_present"])

    def test_missing_directory_is_fail_soft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "does-not-exist"

            summary = summarize_run_directory(run_dir)

            self.assertFalse(summary["complete_safe_noop_run"])
            self.assertEqual(summary["compilation_status"], "unknown")
            self.assertEqual(summary["execution_status"], "unknown")
            self.assertIsNone(summary["review_required"])
            self.assertFalse(summary["blocked_by_review"])
            self.assertFalse(summary["candidate_dir_present"])

    def test_malformed_json_is_fail_soft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            for name in (
                "CompilationReport.json",
                "ExecutionManifest.json",
                "ExecutionResult.json",
                "EffectivePolicy.json",
            ):
                (run_dir / name).write_text("{ not valid json", encoding="utf-8")

            summary = summarize_run_directory(run_dir)

            self.assertEqual(summary["compilation_status"], "unknown")
            self.assertEqual(summary["execution_status"], "unknown")
            self.assertIsNone(summary["review_required"])
            self.assertFalse(summary["blocked_by_review"])

    def test_summary_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            self._completed_run(run_dir)
            before = sorted(p.name for p in run_dir.iterdir())

            summarize_run_directory(run_dir)

            after = sorted(p.name for p in run_dir.iterdir())
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
