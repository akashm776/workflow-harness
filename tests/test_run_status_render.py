from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from orchestrator.safe_run import safe_noop_run
from runtime.run_status import inspect_run_directory
from runtime.run_status_render import render_run_status_text


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"


class RunStatusRenderTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-render-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _make_missing_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-render-test-{uuid4().hex}"
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_complete_approved_run_renders_complete_true_and_all_checked(self) -> None:
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
        rendered = render_run_status_text(status)

        self.assertIn(f"run_dir: {output_dir}", rendered)
        self.assertIn("complete_safe_noop_run: true", rendered)
        self.assertNotIn("[ ]", rendered)
        self.assertIn("[x] CompilationReport.json", rendered)
        self.assertIn("[x] ExecutionResult.json", rendered)

    def test_failed_compile_run_renders_missing_runtime_artifacts_unchecked(self) -> None:
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
        rendered = render_run_status_text(status)

        self.assertIn("complete_safe_noop_run: false", rendered)
        self.assertIn("[x] CompilationReport.json", rendered)
        self.assertIn("[x] CompiledArtifactIndex.json", rendered)
        self.assertIn("[x] AuditLog.jsonl", rendered)
        self.assertIn("[ ] EffectivePolicy.json", rendered)
        self.assertIn("[ ] ExecutionBindings.json", rendered)
        self.assertIn("[ ] ExecutionManifest.json", rendered)
        self.assertIn("[ ] ExecutionResult.json", rendered)

    def test_missing_directory_renders_all_unchecked(self) -> None:
        output_dir = self._make_missing_output_dir()

        status = inspect_run_directory(output_dir)
        rendered = render_run_status_text(status)

        self.assertIn(f"run_dir: {output_dir}", rendered)
        self.assertIn("complete_safe_noop_run: false", rendered)
        self.assertNotIn("[x]", rendered)
        self.assertIn("[ ] CompilationReport.json", rendered)
        self.assertIn("[ ] ExecutionResult.json", rendered)

    def test_renderer_does_not_mutate_input_status(self) -> None:
        output_dir = self._make_missing_output_dir()
        status = inspect_run_directory(output_dir)
        original_status = deepcopy(status)

        render_run_status_text(status)

        self.assertEqual(status, original_status)


if __name__ == "__main__":
    unittest.main()
