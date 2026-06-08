from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from cli.run_status_cli import main
from cli.workflow_demo_cli import run_workflow_demo
from orchestrator.safe_run import safe_noop_run


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"


class RunStatusCliTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-cli-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _make_missing_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-cli-test-{uuid4().hex}"
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _run_cli(self, args: list[str]) -> tuple[int, dict[str, object]]:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(args)
        return exit_code, json.loads(stdout.getvalue())

    def test_approved_safe_noop_run_output_status_cli_exits_zero_and_reports_complete_true(
        self,
    ) -> None:
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

        exit_code, result = self._run_cli(["--run-dir", str(output_dir)])

        self.assertEqual(exit_code, 0)
        self.assertTrue(result["complete_safe_noop_run"])
        self.assertTrue(
            all(
                artifact["exists"]
                for artifact in result["artifacts"].values()
            )
        )

    def test_failed_compile_output_status_cli_exits_one_and_reports_complete_false(
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

        exit_code, result = self._run_cli(["--run-dir", str(output_dir)])

        self.assertEqual(exit_code, 1)
        self.assertFalse(result["complete_safe_noop_run"])
        self.assertTrue(result["artifacts"]["CompilationReport.json"]["exists"])
        self.assertTrue(result["artifacts"]["CompiledArtifactIndex.json"]["exists"])
        self.assertTrue(result["artifacts"]["AuditLog.jsonl"]["exists"])
        self.assertFalse(result["artifacts"]["ExecutionManifest.json"]["exists"])
        self.assertFalse(result["artifacts"]["ExecutionResult.json"]["exists"])

    def test_missing_directory_status_cli_exits_one_and_reports_all_artifacts_false(
        self,
    ) -> None:
        output_dir = self._make_missing_output_dir()

        exit_code, result = self._run_cli(["--run-dir", str(output_dir)])

        self.assertEqual(exit_code, 1)
        self.assertFalse(result["complete_safe_noop_run"])
        self.assertEqual(result["run_dir"], str(output_dir))
        self.assertTrue(
            all(
                artifact["exists"] is False
                for artifact in result["artifacts"].values()
            )
        )

    def test_approved_run_status_cli_text_exits_zero_and_includes_complete_true(
        self,
    ) -> None:
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

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--text"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("complete_safe_noop_run: true", rendered)
        self.assertIn("[x] CompilationReport.json", rendered)
        self.assertIn("[x] ExecutionResult.json", rendered)

    def test_failed_run_status_cli_text_exits_one_and_includes_unchecked_runtime_artifacts(
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

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--text"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("complete_safe_noop_run: false", rendered)
        self.assertIn("[ ] EffectivePolicy.json", rendered)
        self.assertIn("[ ] ExecutionBindings.json", rendered)
        self.assertIn("[ ] ExecutionManifest.json", rendered)
        self.assertIn("[ ] ExecutionResult.json", rendered)

    def test_missing_directory_text_exits_one_and_includes_all_unchecked_artifacts(
        self,
    ) -> None:
        output_dir = self._make_missing_output_dir()

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--text"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("complete_safe_noop_run: false", rendered)
        self.assertNotIn("[x]", rendered)
        self.assertIn("[ ] CompilationReport.json", rendered)
        self.assertIn("[ ] ExecutionResult.json", rendered)

    def test_approved_run_status_cli_view_exits_zero_and_includes_title(self) -> None:
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

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--view"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Safe No-Op Run Status", rendered)
        self.assertIn("complete_safe_noop_run: true", rendered)
        self.assertIn("[x] CompilationReport.json", rendered)

    def test_failed_run_status_cli_view_exits_one_and_includes_unchecked_runtime_artifacts(
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

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--view"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("Safe No-Op Run Status", rendered)
        self.assertIn("[ ] EffectivePolicy.json", rendered)
        self.assertIn("[ ] ExecutionBindings.json", rendered)
        self.assertIn("[ ] ExecutionManifest.json", rendered)
        self.assertIn("[ ] ExecutionResult.json", rendered)

    def test_missing_directory_view_exits_one_and_includes_all_unchecked_artifacts(
        self,
    ) -> None:
        output_dir = self._make_missing_output_dir()

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--view"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("Safe No-Op Run Status", rendered)
        self.assertNotIn("[x]", rendered)
        self.assertIn("[ ] CompilationReport.json", rendered)
        self.assertIn("[ ] ExecutionResult.json", rendered)

    def test_view_takes_precedence_over_text(self) -> None:
        output_dir = self._make_missing_output_dir()

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--text", "--view"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("Safe No-Op Run Status", rendered)
        self.assertNotIn("run_dir:", rendered.splitlines()[0] if rendered else "")

    def test_output_json_has_stable_top_level_keys(self) -> None:
        output_dir = self._make_missing_output_dir()

        _, result = self._run_cli(["--run-dir", str(output_dir)])

        self.assertEqual(
            list(result.keys()),
            [
                "artifacts",
                "complete_safe_noop_run",
                "run_dir",
            ],
        )

    def test_default_json_behavior_remains_unchanged(self) -> None:
        output_dir = self._make_missing_output_dir()

        exit_code, result = self._run_cli(["--run-dir", str(output_dir)])

        self.assertEqual(exit_code, 1)
        self.assertIsInstance(result, dict)
        self.assertIn("artifacts", result)
        self.assertIn("complete_safe_noop_run", result)
        self.assertIn("run_dir", result)

    def test_summary_flag_renders_rich_summary_and_exits_zero(self) -> None:
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

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--summary"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Safe No-Op Run Summary", rendered)
        self.assertIn("compilation_status: compiled", rendered)
        self.assertIn("execution_status: completed", rendered)
        self.assertIn("review_required: false", rendered)
        self.assertIn("blocked_by_review: false", rendered)
        self.assertNotIn("Review Gate:", rendered)
        self.assertIn("status command: python -m cli.run_status_cli", rendered)

    def test_summary_flag_missing_directory_exits_one_and_is_fail_soft(self) -> None:
        output_dir = self._make_missing_output_dir()

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--summary"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("Safe No-Op Run Summary", rendered)
        self.assertIn("compilation_status: unknown", rendered)
        self.assertIn("execution_status: unknown", rendered)

    def test_summary_flag_blocked_run_includes_review_gate_guidance(self) -> None:
        output_dir = self._make_output_dir()
        run_workflow_demo(
            goal="generate innovation ideas from program data",
            node_type_registry_path=SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            run_dir=output_dir,
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--run-dir", str(output_dir), "--summary"])
        rendered = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Safe No-Op Run Summary", rendered)
        self.assertIn("execution_status: blocked", rendered)
        self.assertIn("review_required: true", rendered)
        self.assertIn("blocked_by_review: true", rendered)
        self.assertIn("Review Gate:", rendered)
        self.assertIn("blocked_reason: review_required", rendered)
        self.assertIn("approval_request_count: 1", rendered)
        self.assertIn("approval_request_id:", rendered)
        self.assertIn("node_id: retrieve-1", rendered)
        self.assertIn("reason: Innovation template approval request.", rendered)
        self.assertIn("ApprovalRequests.json", rendered)
        self.assertIn("ApprovalDecisions.json", rendered)
        self.assertIn("this run/request only", rendered)

    def test_default_json_does_not_include_summary_fields(self) -> None:
        output_dir = self._make_missing_output_dir()

        _, result = self._run_cli(["--run-dir", str(output_dir)])

        self.assertNotIn("compilation_status", result)
        self.assertNotIn("execution_status", result)


if __name__ == "__main__":
    unittest.main()
