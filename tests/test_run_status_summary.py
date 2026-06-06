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

    def test_innovation_demo_run_includes_candidate_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="generate innovation ideas from program data",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            candidate_workflow = summarize_run_directory(run_dir)["candidate_workflow"]

            self.assertIsNotNone(candidate_workflow)
            self.assertEqual(len(candidate_workflow["nodes"]), 5)
            self.assertEqual(len(candidate_workflow["edges"]), 4)
            display_names = {
                node.get("display_name") for node in candidate_workflow["nodes"]
            }
            self.assertEqual(
                display_names,
                {
                    "Load Program Data",
                    "Gather Example Context",
                    "Generate Idea Candidates",
                    "Score Against Rubric",
                    "Synthesize MVP Plans",
                },
            )
            node_types = {node["node_type"] for node in candidate_workflow["nodes"]}
            self.assertTrue(node_types.issubset({"retrieve", "synthesize"}))

    def test_missing_candidate_workflow_is_none(self) -> None:
        # A completed safe_noop_run has no candidate/ directory.
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            self._completed_run(run_dir)

            summary = summarize_run_directory(run_dir)
            self.assertIsNone(summary["candidate_workflow"])

    def test_malformed_candidate_workflow_is_fail_soft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            (run_dir / "candidate").mkdir(parents=True)
            (run_dir / "candidate" / "WorkflowSpec.json").write_text(
                "{ not valid json", encoding="utf-8"
            )

            summary = summarize_run_directory(run_dir)
            self.assertIsNone(summary["candidate_workflow"])


if __name__ == "__main__":
    unittest.main()
