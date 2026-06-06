from __future__ import annotations

from pathlib import Path
import json
import shutil
import unittest
from uuid import uuid4

from orchestrator.compile_and_verify import (
    build_execution_manifest_for_orchestration_result,
    compile_write_load_verify,
    write_execution_manifest_for_orchestration_result,
)
from runtime.execution_manifest import build_execution_manifest


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
EMPTY_APPROVAL_DECISIONS = SIMPLE_WORKFLOW / "ApprovalDecisions-empty.json"


class ExecutionManifestTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"execution-manifest-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_approved_verified_node_creates_ready_to_execute_manifest(self) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        manifest = build_execution_manifest(
            node_id=orchestration_result["node_id"],
            workflow_revision_id=orchestration_result["workflow_revision_id"],
            verifier_result=orchestration_result["verifier_result"],
            execution_status="ready_to_execute",
        )

        self.assertEqual(manifest["schema_version"], "m1")
        self.assertEqual(manifest["node_id"], "retrieve-1")
        self.assertEqual(
            manifest["workflow_revision_id"], "workflow-rev-simple-001"
        )
        self.assertEqual(manifest["artifact_lifecycle_state"], "ready_to_run")
        self.assertEqual(manifest["execution_status"], "ready_to_execute")
        self.assertEqual(
            manifest["verifier_result"], {"ok": True, "message": "node may start"}
        )
        self.assertIsNone(manifest["started_at"])
        self.assertIsNone(manifest["completed_at"])
        self.assertEqual(manifest["produced_evidence"], [])
        self.assertEqual(manifest["side_effects"], [])

        orchestration_manifest = build_execution_manifest_for_orchestration_result(
            orchestration_result
        )
        self.assertIsNotNone(orchestration_manifest)
        self.assertEqual(
            orchestration_manifest["execution_status"], "ready_to_execute"
        )
        self.assertEqual(
            orchestration_manifest["artifact_lifecycle_state"], "ready_to_run"
        )

        write_result = write_execution_manifest_for_orchestration_result(
            orchestration_result,
            output_dir,
        )
        self.assertTrue(write_result["execution_manifest_written"])
        self.assertEqual(
            Path(write_result["execution_manifest_path"]).name,
            "ExecutionManifest.json",
        )
        self.assertTrue((output_dir / "ExecutionManifest.json").exists())
        reloaded_manifest = json.loads(
            (output_dir / "ExecutionManifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(reloaded_manifest, write_result["execution_manifest"])
        self.assertEqual(reloaded_manifest["execution_status"], "ready_to_execute")

    def test_unapproved_skipped_path_creates_blocked_manifest(self) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
            approval_decisions_path=EMPTY_APPROVAL_DECISIONS,
        )

        manifest = build_execution_manifest(
            node_id=orchestration_result["node_id"],
            workflow_revision_id=orchestration_result["workflow_revision_id"],
            verifier_result=orchestration_result["verifier_result"],
            execution_status="blocked",
        )

        self.assertEqual(manifest["artifact_lifecycle_state"], "failed")
        self.assertEqual(manifest["execution_status"], "blocked")
        self.assertIsNone(manifest["verifier_result"])

        orchestration_manifest = build_execution_manifest_for_orchestration_result(
            orchestration_result
        )
        self.assertIsNotNone(orchestration_manifest)
        self.assertEqual(orchestration_manifest["execution_status"], "blocked")
        self.assertEqual(orchestration_manifest["artifact_lifecycle_state"], "failed")

        write_result = write_execution_manifest_for_orchestration_result(
            orchestration_result,
            output_dir,
        )
        self.assertTrue(write_result["execution_manifest_written"])
        reloaded_manifest = json.loads(
            (output_dir / "ExecutionManifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(reloaded_manifest["execution_status"], "blocked")
        self.assertEqual(reloaded_manifest["artifact_lifecycle_state"], "failed")

    def test_execution_status_and_artifact_lifecycle_state_are_distinct(self) -> None:
        ready_manifest = build_execution_manifest(
            node_id="retrieve-1",
            workflow_revision_id="workflow-rev-simple-001",
            verifier_result={"ok": True, "message": "node may start"},
            execution_status="ready_to_execute",
        )
        blocked_manifest = build_execution_manifest(
            node_id="retrieve-1",
            workflow_revision_id="workflow-rev-simple-001",
            verifier_result=None,
            execution_status="blocked",
        )

        self.assertEqual(ready_manifest["execution_status"], "ready_to_execute")
        self.assertEqual(ready_manifest["artifact_lifecycle_state"], "ready_to_run")
        self.assertNotEqual(
            ready_manifest["execution_status"],
            ready_manifest["artifact_lifecycle_state"],
        )
        self.assertEqual(blocked_manifest["execution_status"], "blocked")
        self.assertEqual(blocked_manifest["artifact_lifecycle_state"], "failed")
        self.assertNotEqual(
            blocked_manifest["execution_status"],
            blocked_manifest["artifact_lifecycle_state"],
        )

    def test_failed_compile_path_does_not_create_execution_manifest_yet(self) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            UNKNOWN_NODE_TYPE / "WorkflowSpec.json",
            UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json",
            UNKNOWN_NODE_TYPE / "RequestedAuth.json",
            UNKNOWN_NODE_TYPE / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        self.assertFalse(orchestration_result["compile_summary"]["ok"])
        self.assertIsNone(
            build_execution_manifest_for_orchestration_result(orchestration_result)
        )
        write_result = write_execution_manifest_for_orchestration_result(
            orchestration_result,
            output_dir,
        )
        self.assertFalse(write_result["execution_manifest_written"])
        self.assertFalse((output_dir / "ExecutionManifest.json").exists())

    def test_verifier_failure_path_creates_blocked_manifest(self) -> None:
        orchestration_result = {
            "workflow_revision_id": "workflow-rev-simple-001",
            "node_id": "retrieve-1",
            "compile_summary": {
                "ok": True,
                "emitted_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
                "compilation_status": "compiled",
                "diagnostics": [],
                "may_runtime_start_possible": True,
            },
            "write_manifest": {
                "ok": True,
                "output_dir": str(self._make_output_dir()),
                "written_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
            },
            "load_result_ok": True,
            "verifier_result": {
                "ok": False,
                "message": "effective policy artifact revision mismatch",
            },
        }

        manifest = build_execution_manifest_for_orchestration_result(
            orchestration_result
        )

        self.assertIsNotNone(manifest)
        self.assertEqual(manifest["execution_status"], "blocked")
        self.assertEqual(manifest["artifact_lifecycle_state"], "failed")
        self.assertEqual(
            manifest["verifier_result"],
            {
                "ok": False,
                "message": "effective policy artifact revision mismatch",
            },
        )


if __name__ == "__main__":
    unittest.main()
