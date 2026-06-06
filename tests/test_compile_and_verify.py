from __future__ import annotations

from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from orchestrator.compile_and_verify import (
    build_orchestration_audit_events,
    compile_write_load_verify,
)


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
CONFLICTING_APPROVAL_FIXTURE = (
    ROOT / "fixtures" / "invalid" / "conflicting-approval-decisions" / "input"
)
EMPTY_APPROVAL_DECISIONS = SIMPLE_WORKFLOW / "ApprovalDecisions-empty.json"


class CompileAndVerifyTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"compile-and-verify-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_approved_valid_workflow_compiles_writes_loads_and_verifies_true(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        self.assertTrue(result["compile_summary"]["ok"])
        self.assertTrue(result["compile_summary"]["may_runtime_start_possible"])
        self.assertEqual(result["workflow_revision_id"], "workflow-rev-simple-001")
        self.assertEqual(result["node_id"], "retrieve-1")
        self.assertEqual(result["write_manifest"]["written_artifacts"], [
            "CompilationReport.json",
            "CompiledArtifactIndex.json",
            "EffectivePolicy.json",
            "ExecutionBindings.json",
        ])
        self.assertTrue(result["load_result_ok"])
        self.assertEqual(
            result["verifier_result"], {"ok": True, "message": "node may start"}
        )

        audit_events = build_orchestration_audit_events(result)
        self.assertEqual(
            [event["event_type"] for event in audit_events],
            [
                "compile_completed",
                "artifacts_written",
                "runtime_verification_completed",
            ],
        )

    def test_unapproved_workflow_compiles_and_writes_but_does_not_verify_start(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
            approval_decisions_path=EMPTY_APPROVAL_DECISIONS,
        )

        self.assertTrue(result["compile_summary"]["ok"])
        self.assertFalse(result["compile_summary"]["may_runtime_start_possible"])
        self.assertEqual(result["write_manifest"]["written_artifacts"], [
            "CompilationReport.json",
            "CompiledArtifactIndex.json",
            "EffectivePolicy.json",
            "ExecutionBindings.json",
        ])
        self.assertFalse(result["load_result_ok"])
        self.assertIsNone(result["verifier_result"])

        audit_events = build_orchestration_audit_events(result)
        self.assertEqual(
            [event["event_type"] for event in audit_events],
            [
                "compile_completed",
                "artifacts_written",
                "runtime_verification_skipped",
            ],
        )

    def test_unknown_node_type_workflow_writes_failed_artifacts_and_does_not_verify_start(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        result = compile_write_load_verify(
            UNKNOWN_NODE_TYPE / "WorkflowSpec.json",
            UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json",
            UNKNOWN_NODE_TYPE / "RequestedAuth.json",
            UNKNOWN_NODE_TYPE / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        self.assertFalse(result["compile_summary"]["ok"])
        self.assertEqual(result["compile_summary"]["compilation_status"], "failed")
        self.assertFalse(result["compile_summary"]["may_runtime_start_possible"])
        self.assertEqual(result["write_manifest"]["written_artifacts"], [
            "CompilationReport.json",
            "CompiledArtifactIndex.json",
        ])
        self.assertFalse(result["load_result_ok"])
        self.assertIsNone(result["verifier_result"])

        audit_events = build_orchestration_audit_events(result)
        self.assertEqual(
            [event["event_type"] for event in audit_events],
            [
                "compile_failed",
                "artifacts_written",
                "runtime_verification_skipped",
            ],
        )

    def test_conflicting_approval_decisions_writes_failed_artifacts_and_does_not_verify_start(
        self,
    ) -> None:
        output_dir = self._make_output_dir()

        result = compile_write_load_verify(
            CONFLICTING_APPROVAL_FIXTURE / "WorkflowSpec.json",
            CONFLICTING_APPROVAL_FIXTURE / "NodeTypeRegistry.json",
            CONFLICTING_APPROVAL_FIXTURE / "RequestedAuth.json",
            CONFLICTING_APPROVAL_FIXTURE / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        self.assertFalse(result["compile_summary"]["ok"])
        self.assertEqual(result["compile_summary"]["compilation_status"], "failed")
        self.assertEqual(
            result["compile_summary"]["diagnostics"][0]["error_code"],
            "CONFLICTING_APPROVAL_DECISIONS",
        )
        self.assertFalse(result["compile_summary"]["may_runtime_start_possible"])
        self.assertEqual(result["write_manifest"]["written_artifacts"], [
            "CompilationReport.json",
            "CompiledArtifactIndex.json",
        ])
        self.assertFalse(result["load_result_ok"])
        self.assertIsNone(result["verifier_result"])

        audit_events = build_orchestration_audit_events(result)
        self.assertEqual(
            [event["event_type"] for event in audit_events],
            [
                "compile_failed",
                "artifacts_written",
                "runtime_verification_skipped",
            ],
        )


if __name__ == "__main__":
    unittest.main()
