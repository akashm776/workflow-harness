from __future__ import annotations

from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from orchestrator.safe_run import safe_noop_run
from runtime.run_status import inspect_run_directory


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
EMPTY_APPROVAL_DECISIONS = SIMPLE_WORKFLOW / "ApprovalDecisions-empty.json"


class RunStatusTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _make_missing_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-test-{uuid4().hex}"
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_approved_safe_noop_run_reports_all_files_and_complete_true(self) -> None:
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

        self.assertEqual(status["run_dir"], str(output_dir))
        self.assertTrue(status["complete_safe_noop_run"])
        self.assertTrue(
            all(
                artifact["exists"]
                for artifact in status["artifacts"].values()
            )
        )

    def test_unapproved_safe_noop_run_reports_all_files_and_complete_true(self) -> None:
        output_dir = self._make_output_dir()
        safe_noop_run(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
            approval_decisions_path=EMPTY_APPROVAL_DECISIONS,
        )

        status = inspect_run_directory(output_dir)

        self.assertTrue(status["complete_safe_noop_run"])
        self.assertTrue(
            all(
                artifact["exists"]
                for artifact in status["artifacts"].values()
            )
        )

    def test_failed_compile_reports_only_compile_artifacts_and_audit_log_and_complete_false(
        self,
    ) -> None:
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

        self.assertFalse(status["complete_safe_noop_run"])
        self.assertTrue(status["artifacts"]["CompilationReport.json"]["exists"])
        self.assertTrue(status["artifacts"]["CompiledArtifactIndex.json"]["exists"])
        self.assertTrue(status["artifacts"]["AuditLog.jsonl"]["exists"])
        self.assertFalse(status["artifacts"]["EffectivePolicy.json"]["exists"])
        self.assertFalse(status["artifacts"]["ExecutionBindings.json"]["exists"])
        self.assertFalse(status["artifacts"]["ExecutionManifest.json"]["exists"])
        self.assertFalse(status["artifacts"]["ExecutionResult.json"]["exists"])

    def test_missing_directory_reports_all_artifacts_false_and_complete_false(
        self,
    ) -> None:
        output_dir = self._make_missing_output_dir()

        status = inspect_run_directory(output_dir)

        self.assertEqual(status["run_dir"], str(output_dir))
        self.assertFalse(status["complete_safe_noop_run"])
        self.assertTrue(
            all(
                artifact["exists"] is False
                for artifact in status["artifacts"].values()
            )
        )


if __name__ == "__main__":
    unittest.main()
