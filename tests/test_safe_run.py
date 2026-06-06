from __future__ import annotations

import json
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from orchestrator.safe_run import safe_noop_run


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
EMPTY_APPROVAL_DECISIONS = SIMPLE_WORKFLOW / "ApprovalDecisions-empty.json"


class SafeRunTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"safe-run-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_approved_workflow_writes_compiled_artifacts_audit_log_manifest_and_result(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        result = safe_noop_run(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        self.assertEqual(
            list(result.keys()),
            [
                "orchestration_result",
                "audit_log_result",
                "execution_manifest_write_result",
                "noop_execution",
                "execution_result_write_result",
            ],
        )
        self.assertTrue(result["orchestration_result"]["compile_summary"]["ok"])
        self.assertTrue(
            result["orchestration_result"]["compile_summary"][
                "may_runtime_start_possible"
            ]
        )
        self.assertTrue((output_dir / "AuditLog.jsonl").exists())
        self.assertTrue((output_dir / "ExecutionManifest.json").exists())
        self.assertTrue((output_dir / "ExecutionResult.json").exists())

        manifest = json.loads(
            (output_dir / "ExecutionManifest.json").read_text(encoding="utf-8")
        )
        execution_result = json.loads(
            (output_dir / "ExecutionResult.json").read_text(encoding="utf-8")
        )
        audit_lines = (
            output_dir / "AuditLog.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        audit_events = [json.loads(line) for line in audit_lines]

        self.assertEqual(manifest["execution_status"], "ready_to_execute")
        self.assertEqual(manifest["artifact_lifecycle_state"], "ready_to_run")
        self.assertEqual(execution_result["execution_status"], "completed")
        self.assertEqual(
            [event["event_type"] for event in audit_events],
            [
                "compile_completed",
                "artifacts_written",
                "runtime_verification_completed",
            ],
        )

    def test_unapproved_workflow_writes_blocked_manifest_and_blocked_result(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        result = safe_noop_run(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
            approval_decisions_path=EMPTY_APPROVAL_DECISIONS,
        )

        self.assertTrue(result["orchestration_result"]["compile_summary"]["ok"])
        self.assertFalse(
            result["orchestration_result"]["compile_summary"][
                "may_runtime_start_possible"
            ]
        )
        self.assertIsNone(result["orchestration_result"]["verifier_result"])
        self.assertTrue((output_dir / "AuditLog.jsonl").exists())
        self.assertTrue((output_dir / "ExecutionManifest.json").exists())
        self.assertTrue((output_dir / "ExecutionResult.json").exists())

        manifest = json.loads(
            (output_dir / "ExecutionManifest.json").read_text(encoding="utf-8")
        )
        execution_result = json.loads(
            (output_dir / "ExecutionResult.json").read_text(encoding="utf-8")
        )
        audit_events = [
            json.loads(line)
            for line in (output_dir / "AuditLog.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]

        self.assertEqual(manifest["execution_status"], "blocked")
        self.assertEqual(manifest["artifact_lifecycle_state"], "failed")
        self.assertEqual(execution_result["execution_status"], "blocked")
        self.assertEqual(
            [event["event_type"] for event in audit_events],
            [
                "compile_completed",
                "artifacts_written",
                "runtime_verification_skipped",
            ],
        )

    def test_failed_compile_writes_failed_artifacts_and_audit_log_but_no_manifest_or_result(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        result = safe_noop_run(
            UNKNOWN_NODE_TYPE / "WorkflowSpec.json",
            UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json",
            UNKNOWN_NODE_TYPE / "RequestedAuth.json",
            UNKNOWN_NODE_TYPE / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        self.assertFalse(result["orchestration_result"]["compile_summary"]["ok"])
        self.assertTrue((output_dir / "CompilationReport.json").exists())
        self.assertTrue((output_dir / "CompiledArtifactIndex.json").exists())
        self.assertTrue((output_dir / "AuditLog.jsonl").exists())
        self.assertFalse((output_dir / "ExecutionManifest.json").exists())
        self.assertFalse((output_dir / "ExecutionResult.json").exists())
        self.assertFalse(
            result["execution_manifest_write_result"]["execution_manifest_written"]
        )
        self.assertIsNone(result["noop_execution"])
        self.assertIsNone(result["execution_result_write_result"])


if __name__ == "__main__":
    unittest.main()
