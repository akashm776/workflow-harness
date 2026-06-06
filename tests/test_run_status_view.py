from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from orchestrator.safe_run import safe_noop_run
from runtime.run_status import inspect_run_directory
from tui.run_status_view import build_run_status_view_model, render_run_status_view


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"


class RunStatusViewTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-view-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _make_missing_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-view-test-{uuid4().hex}"
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_approved_run_model_has_all_rows_true_and_complete_true(self) -> None:
        output_dir = self._make_output_dir()
        safe_noop_run(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        status = inspect_run_directory(output_dir)
        view_model = build_run_status_view_model(status)

        self.assertEqual(view_model["title"], "Safe No-Op Run Status")
        self.assertEqual(view_model["run_dir"], str(output_dir))
        self.assertTrue(view_model["complete_safe_noop_run"])
        self.assertTrue(all(row["exists"] for row in view_model["rows"]))
        self.assertTrue(all(row["marker"] == "[x]" for row in view_model["rows"]))

    def test_failed_compile_model_has_runtime_artifacts_false(self) -> None:
        output_dir = self._make_output_dir()
        safe_noop_run(
            UNKNOWN_NODE_TYPE / "WorkflowSpec.json",
            UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json",
            UNKNOWN_NODE_TYPE / "RequestedAuth.json",
            UNKNOWN_NODE_TYPE / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        status = inspect_run_directory(output_dir)
        view_model = build_run_status_view_model(status)
        row_by_artifact = {
            row["artifact"]: row
            for row in view_model["rows"]
        }

        self.assertFalse(view_model["complete_safe_noop_run"])
        self.assertFalse(row_by_artifact["EffectivePolicy.json"]["exists"])
        self.assertFalse(row_by_artifact["ExecutionBindings.json"]["exists"])
        self.assertFalse(row_by_artifact["ExecutionManifest.json"]["exists"])
        self.assertFalse(row_by_artifact["ExecutionResult.json"]["exists"])
        self.assertEqual(row_by_artifact["EffectivePolicy.json"]["marker"], "[ ]")

    def test_missing_directory_model_has_all_rows_false(self) -> None:
        output_dir = self._make_missing_output_dir()

        status = inspect_run_directory(output_dir)
        view_model = build_run_status_view_model(status)

        self.assertFalse(view_model["complete_safe_noop_run"])
        self.assertTrue(all(row["exists"] is False for row in view_model["rows"]))
        self.assertTrue(all(row["marker"] == "[ ]" for row in view_model["rows"]))

    def test_render_output_includes_title_run_dir_and_artifact_rows(self) -> None:
        output_dir = self._make_missing_output_dir()

        status = inspect_run_directory(output_dir)
        rendered = render_run_status_view(status)

        self.assertIn("Safe No-Op Run Status", rendered)
        self.assertIn(f"run_dir: {output_dir}", rendered)
        self.assertIn("complete_safe_noop_run: false", rendered)
        self.assertIn("[ ] CompilationReport.json", rendered)
        self.assertIn("[ ] ExecutionResult.json", rendered)

    def test_renderer_and_model_do_not_mutate_input_status(self) -> None:
        output_dir = self._make_missing_output_dir()
        status = inspect_run_directory(output_dir)
        original_status = deepcopy(status)

        build_run_status_view_model(status)
        render_run_status_view(status)

        self.assertEqual(status, original_status)


if __name__ == "__main__":
    unittest.main()
