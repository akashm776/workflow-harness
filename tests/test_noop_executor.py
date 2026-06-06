from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from orchestrator.compile_and_verify import (
    compile_write_load_verify,
    execute_noop_for_orchestration_result,
)
from runtime.execution_manifest import build_execution_manifest
from runtime.noop_executor import execute_noop_node


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
EMPTY_APPROVAL_DECISIONS = SIMPLE_WORKFLOW / "ApprovalDecisions-empty.json"


class NoopExecutorTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"noop-executor-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_ready_to_execute_manifest_returns_completed(self) -> None:
        execution_manifest = build_execution_manifest(
            node_id="retrieve-1",
            workflow_revision_id="workflow-rev-simple-001",
            verifier_result={"ok": True, "message": "node may start"},
            execution_status="ready_to_execute",
        )

        result = execute_noop_node(execution_manifest)

        self.assertEqual(
            result,
            {
                "ok": True,
                "execution_status": "completed",
                "produced_evidence": [],
                "side_effects": [],
            },
        )

    def test_blocked_manifest_returns_blocked(self) -> None:
        execution_manifest = build_execution_manifest(
            node_id="retrieve-1",
            workflow_revision_id="workflow-rev-simple-001",
            verifier_result=None,
            execution_status="blocked",
        )

        result = execute_noop_node(execution_manifest)

        self.assertEqual(
            result,
            {
                "ok": False,
                "execution_status": "blocked",
                "produced_evidence": [],
                "side_effects": [],
            },
        )

    def test_input_manifest_is_not_mutated(self) -> None:
        execution_manifest = build_execution_manifest(
            node_id="retrieve-1",
            workflow_revision_id="workflow-rev-simple-001",
            verifier_result={"ok": True, "message": "node may start"},
            execution_status="ready_to_execute",
        )
        original_manifest = dict(execution_manifest)
        original_manifest["produced_evidence"] = list(execution_manifest["produced_evidence"])
        original_manifest["side_effects"] = list(execution_manifest["side_effects"])

        execute_noop_node(execution_manifest)

        self.assertEqual(execution_manifest, original_manifest)

    def test_produced_evidence_and_side_effects_remain_empty(self) -> None:
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

        ready_result = execute_noop_node(ready_manifest)
        blocked_result = execute_noop_node(blocked_manifest)

        self.assertEqual(ready_result["produced_evidence"], [])
        self.assertEqual(ready_result["side_effects"], [])
        self.assertEqual(blocked_result["produced_evidence"], [])
        self.assertEqual(blocked_result["side_effects"], [])

    def test_orchestration_helper_returns_completed_for_approved_workflow(self) -> None:
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

        result = execute_noop_for_orchestration_result(orchestration_result)

        self.assertIsNotNone(result)
        self.assertEqual(
            result["execution_manifest"]["execution_status"], "ready_to_execute"
        )
        self.assertEqual(
            result["execution_result"],
            {
                "ok": True,
                "execution_status": "completed",
                "produced_evidence": [],
                "side_effects": [],
            },
        )

    def test_orchestration_helper_returns_blocked_for_unapproved_workflow(self) -> None:
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

        result = execute_noop_for_orchestration_result(orchestration_result)

        self.assertIsNotNone(result)
        self.assertEqual(result["execution_manifest"]["execution_status"], "blocked")
        self.assertEqual(
            result["execution_result"],
            {
                "ok": False,
                "execution_status": "blocked",
                "produced_evidence": [],
                "side_effects": [],
            },
        )

    def test_orchestration_helper_returns_none_for_failed_compile(self) -> None:
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

        result = execute_noop_for_orchestration_result(orchestration_result)

        self.assertIsNone(result)

    def test_orchestration_result_is_not_mutated(self) -> None:
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
        original_result = deepcopy(orchestration_result)

        execute_noop_for_orchestration_result(orchestration_result)

        self.assertEqual(orchestration_result, original_result)


if __name__ == "__main__":
    unittest.main()
