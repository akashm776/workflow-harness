from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from cli.safe_run_cli import main


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
EMPTY_APPROVAL_DECISIONS = SIMPLE_WORKFLOW / "ApprovalDecisions-empty.json"


class SafeRunCliTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"safe-run-cli-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _make_output_dir_path(self) -> Path:
        output_dir = ROOT / f"safe-run-cli-test-{uuid4().hex}"
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _run_cli(self, args: list[str]) -> tuple[int, dict[str, object]]:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(args)
        return exit_code, json.loads(stdout.getvalue())

    def test_approved_workflow_cli_returns_zero_and_writes_expected_files(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        exit_code, summary = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue(summary["orchestration_result"]["compile_summary"]["ok"])
        self.assertTrue(
            summary["orchestration_result"]["compile_summary"][
                "may_runtime_start_possible"
            ]
        )
        self.assertTrue((output_dir / "CompilationReport.json").exists())
        self.assertTrue((output_dir / "CompiledArtifactIndex.json").exists())
        self.assertTrue((output_dir / "EffectivePolicy.json").exists())
        self.assertTrue((output_dir / "ExecutionBindings.json").exists())
        self.assertTrue((output_dir / "AuditLog.jsonl").exists())
        self.assertTrue((output_dir / "ExecutionManifest.json").exists())
        self.assertTrue((output_dir / "ExecutionResult.json").exists())

    def test_approved_workflow_summary_only_returns_compact_summary_with_completed_execution_status(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        exit_code, summary = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--summary-only",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            summary,
            {
                "audit_log_path": str(output_dir / "AuditLog.jsonl"),
                "compilation_status": "compiled",
                "emitted_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
                "execution_status": "completed",
                "may_runtime_start_possible": True,
                "ok": True,
                "output_dir": str(output_dir),
            },
        )

    def test_unapproved_workflow_cli_returns_zero_but_reports_blocked_runtime_start(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        exit_code, summary = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--approval-decisions",
                str(EMPTY_APPROVAL_DECISIONS),
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue(summary["orchestration_result"]["compile_summary"]["ok"])
        self.assertFalse(
            summary["orchestration_result"]["compile_summary"][
                "may_runtime_start_possible"
            ]
        )
        self.assertIsNone(summary["orchestration_result"]["verifier_result"])
        self.assertEqual(
            summary["noop_execution"]["execution_result"]["execution_status"],
            "blocked",
        )
        self.assertTrue((output_dir / "AuditLog.jsonl").exists())
        self.assertTrue((output_dir / "ExecutionManifest.json").exists())
        self.assertTrue((output_dir / "ExecutionResult.json").exists())

    def test_unapproved_workflow_summary_only_returns_compact_summary_with_blocked_execution_status(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        exit_code, summary = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--approval-decisions",
                str(EMPTY_APPROVAL_DECISIONS),
                "--summary-only",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            summary,
            {
                "audit_log_path": str(output_dir / "AuditLog.jsonl"),
                "compilation_status": "compiled",
                "emitted_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
                "execution_status": "blocked",
                "may_runtime_start_possible": False,
                "ok": True,
                "output_dir": str(output_dir),
            },
        )

    def test_unknown_node_type_workflow_cli_returns_one_and_writes_failed_artifacts_and_audit_log(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        exit_code, summary = self._run_cli(
            [
                "--workflow-spec",
                str(UNKNOWN_NODE_TYPE / "WorkflowSpec.json"),
                "--node-type-registry",
                str(UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(UNKNOWN_NODE_TYPE / "RequestedAuth.json"),
                "--approval-requests",
                str(UNKNOWN_NODE_TYPE / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
            ]
        )

        self.assertEqual(exit_code, 1)
        self.assertFalse(summary["orchestration_result"]["compile_summary"]["ok"])
        self.assertTrue((output_dir / "CompilationReport.json").exists())
        self.assertTrue((output_dir / "CompiledArtifactIndex.json").exists())
        self.assertTrue((output_dir / "AuditLog.jsonl").exists())
        self.assertFalse((output_dir / "ExecutionManifest.json").exists())
        self.assertFalse((output_dir / "ExecutionResult.json").exists())

    def test_failed_compile_summary_only_returns_compact_summary_without_execution_status(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        exit_code, summary = self._run_cli(
            [
                "--workflow-spec",
                str(UNKNOWN_NODE_TYPE / "WorkflowSpec.json"),
                "--node-type-registry",
                str(UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(UNKNOWN_NODE_TYPE / "RequestedAuth.json"),
                "--approval-requests",
                str(UNKNOWN_NODE_TYPE / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--summary-only",
            ]
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            summary,
            {
                "audit_log_path": str(output_dir / "AuditLog.jsonl"),
                "compilation_status": "failed",
                "emitted_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                ],
                "may_runtime_start_possible": False,
                "ok": False,
                "output_dir": str(output_dir),
            },
        )

    def test_default_cli_behavior_remains_unchanged(self) -> None:
        output_dir = self._make_output_dir()

        _, summary = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
            ]
        )

        self.assertEqual(
            list(summary.keys()),
            [
                "audit_log_result",
                "execution_manifest_write_result",
                "execution_result_write_result",
                "noop_execution",
                "orchestration_result",
            ],
        )

    def test_approved_workflow_dry_run_exits_zero_and_writes_no_output_files(
        self,
    ) -> None:
        output_dir = self._make_output_dir_path()

        exit_code, result = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--dry-run",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue(result["dry_run"])
        self.assertTrue(result["compile_summary"]["ok"])
        self.assertFalse(output_dir.exists())

    def test_failed_workflow_dry_run_exits_one_and_writes_no_output_files(self) -> None:
        output_dir = self._make_output_dir_path()

        exit_code, result = self._run_cli(
            [
                "--workflow-spec",
                str(UNKNOWN_NODE_TYPE / "WorkflowSpec.json"),
                "--node-type-registry",
                str(UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(UNKNOWN_NODE_TYPE / "RequestedAuth.json"),
                "--approval-requests",
                str(UNKNOWN_NODE_TYPE / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--dry-run",
            ]
        )

        self.assertEqual(exit_code, 1)
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["compile_summary"]["ok"])
        self.assertFalse(output_dir.exists())

    def test_dry_run_summary_only_prints_compact_summary(self) -> None:
        output_dir = self._make_output_dir_path()

        exit_code, summary = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--dry-run",
                "--summary-only",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            summary,
            {
                "compilation_status": "compiled",
                "emitted_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
                "may_runtime_start_possible": True,
                "ok": True,
                "output_dir": str(output_dir),
            },
        )
        self.assertFalse(output_dir.exists())

    def test_approved_workflow_check_exits_zero_and_writes_no_output_dir(
        self,
    ) -> None:
        output_dir = self._make_output_dir_path()

        exit_code, result = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--check",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            result,
            {
                "ok": True,
                "compilation_status": "compiled",
                "diagnostics": [],
            },
        )
        self.assertFalse(output_dir.exists())

    def test_failed_workflow_check_exits_one_and_includes_diagnostics(self) -> None:
        output_dir = self._make_output_dir_path()

        exit_code, result = self._run_cli(
            [
                "--workflow-spec",
                str(UNKNOWN_NODE_TYPE / "WorkflowSpec.json"),
                "--node-type-registry",
                str(UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(UNKNOWN_NODE_TYPE / "RequestedAuth.json"),
                "--approval-requests",
                str(UNKNOWN_NODE_TYPE / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--check",
            ]
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["compilation_status"], "failed")
        self.assertGreater(len(result["diagnostics"]), 0)
        self.assertEqual(
            result["diagnostics"][0]["error_code"],
            "UNKNOWN_NODE_TYPE",
        )
        self.assertFalse(output_dir.exists())

    def test_check_summary_only_still_prints_check_shaped_output(self) -> None:
        output_dir = self._make_output_dir_path()

        exit_code, result = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--check",
                "--summary-only",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            result,
            {
                "ok": True,
                "compilation_status": "compiled",
                "diagnostics": [],
            },
        )
        self.assertFalse(output_dir.exists())

    def test_normal_dry_run_behavior_remains_unchanged(self) -> None:
        output_dir = self._make_output_dir_path()

        exit_code, result = self._run_cli(
            [
                "--workflow-spec",
                str(SIMPLE_WORKFLOW / "WorkflowSpec.json"),
                "--node-type-registry",
                str(SIMPLE_WORKFLOW / "NodeTypeRegistry.json"),
                "--requested-auth",
                str(SIMPLE_WORKFLOW / "RequestedAuth.json"),
                "--approval-requests",
                str(SIMPLE_WORKFLOW / "ApprovalRequests.json"),
                "--repo-root",
                str(ROOT),
                "--output-dir",
                str(output_dir),
                "--node-id",
                "retrieve-1",
                "--dry-run",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            list(result.keys()),
            [
                "compile_result",
                "compile_summary",
                "dry_run",
                "output_dir",
            ],
        )
        self.assertTrue(result["dry_run"])
        self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
